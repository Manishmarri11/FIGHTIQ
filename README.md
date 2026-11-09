# FIGHTIQ — UFC Fight Outcome Predictor

A full-stack web app that predicts the outcome of a UFC matchup. Pick two fighters,
get a predicted winner with win probabilities, and save matchups to your account.

Built around a scikit-learn model trained on 6,528 historical UFC fights, served
through a FastAPI REST API backed by PostgreSQL, with a React frontend.

![Fighter list](docs/screenshots/fighters.png)

---

## Features

- **Fighter database** — 2,112 fighters with search, weight-class filtering, and pagination
- **Fighter profiles** — a detail page per fighter with their actual UFC record, physical stats, and the inputs the model sees
- **Matchup prediction** — side-by-side stat comparison plus predicted winner and win probabilities
- **Authentication** — JWT-based signup and login with bcrypt-hashed passwords
- **Saved comparisons** — logged-in users can save, list, and delete matchups, scoped to their account
- **Tested** — pytest suite for the API, run in GitHub Actions together with the frontend lint and build

## Screenshots

**Comparison with prediction**

![Comparison page](docs/screenshots/comparison.png)

**Authentication**

![Login page](docs/screenshots/login.png)

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, React Router, Axios |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic, psycopg 3 |
| Database | PostgreSQL 16 |
| ML | scikit-learn (scaled Logistic Regression pipeline), pandas |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Testing | pytest + FastAPI TestClient (in-memory SQLite), GitHub Actions |
| Infra | Docker Compose (local Postgres), Render, Vercel |

## Data & credits

Fight data comes from the [**Ultimate UFC Dataset**](https://www.kaggle.com/datasets/mdabbert/ultimate-ufc-dataset)
by **mdabbert** on Kaggle. All credit for collecting and maintaining the data goes to
its author. The dataset is not redistributed in this repository; see
[Dataset](#dataset) for how to download it.

## Architecture

```
React SPA  ──── HTTP / JSON ────>  FastAPI  ──── SQL ────>  PostgreSQL
(Vercel)                          (Render)                  (Render)
                                      │
                                      └──> ufc_ml.pkl  (trained model, loaded once at startup)
```

The frontend holds no business logic. The API owns prediction, validation, and
auth; PostgreSQL persists fighters, users, and saved comparisons.

---

## The model

A scikit-learn pipeline (mean imputation → standard scaling → logistic regression)
trained on 28 features per fight: betting odds and expected value, current
win/lose streaks, wins by KO / submission / decision type, and physical attributes
(height, reach, weight) for both fighters. Scores on a held-out 25% of fights:

| Model | Accuracy | F1 | Precision | ROC AUC |
|---|---|---|---|---|
| Baseline: always pick Red | 0.593 | 0.744 | 0.593 | 0.500 |
| Without betting-odds features | 0.603 | 0.718 | 0.620 | 0.598 |
| **Full model (served)** | **0.665** | **0.742** | **0.682** | **0.702** |

Training lives in [`project.py`](project.py) (`python project.py` from the repo
root). It prints all three rows and writes `backend/ml/ufc_ml.pkl`. The API loads
that pickle and never retrains.

**On interpreting these numbers:** the baseline matters more than the raw accuracy.
Red wins 59% of the held-out fights, so a model that always says "Red" already scores
0.593. Without betting odds, fighter attributes alone barely beat that (0.603).
Nearly all of the model's lift comes from the odds, which already encode the
market's forecast. The honest framing is "a calibrated read of the market plus
fighter stats," not "beats the bookmakers." F1 also looks flattering because
"Red wins" is the majority class, which is why ROC AUC is reported too.

Because the imputer and scaler live inside the pickled pipeline, the API passes
raw stats with missing values as `NaN`, and they are filled exactly as in training.
(The original app filled them with `0`, which the model had never seen during
training.) `scikit-learn` is pinned in `requirements.txt` because pickles are not
portable across versions.

### Turning fight rows into fighter profiles

The source dataset is **fight-level**: each row is one Red-vs-Blue matchup with both
fighters' stats frozen at that point in time. There is no fighter table and no
fighter ID — only names repeated across rows.

[`seed_fighters.py`](backend/app/scripts/seed_fighters.py) reshapes this once at
setup: for each of the 2,112 unique fighters it collects every fight they appear in
(from either corner), averages their own stats, and takes their most recent fight
for point-in-time attributes like weight class and stance. Its actual UFC record is
the win/loss count going into its most recent fight plus that fight's result. The
result is one row per fighter, which the prediction endpoint reads directly instead of re-parsing a 2.9 MB
CSV on every request.

### Corner assignment

The model was trained with `Winner` encoded as Red = 1, Blue = 0, so it only knows
how to score "Red vs Blue". In the data, Red wins 58% of fights (Red is usually the
favoured or higher-ranked fighter), so the model has learned a Red-corner bias.

A hypothetical matchup has no corner. The original app assigned corners by sorting
names alphabetically, which meant the corner, and sometimes the predicted winner,
depended on spelling: Alex Pereira scored 53% against Israel Adesanya as Red and 43%
as Blue. The API now scores each matchup both ways and averages the two:

```
P(A wins) = ( P(Red wins | A is Red) + P(Blue wins | A is Blue) ) / 2
```

The result is independent of the order the fighters are given in, and the corner
bias cancels out.

---

## API

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | — | Health check |
| `GET` | `/fighters` | — | List fighters (`search`, `weight_class`, `page`, `page_size`) |
| `GET` | `/fighters/{id}` | — | Single fighter |
| `POST` | `/predict` | — | Predict a matchup from two fighter IDs |
| `POST` | `/auth/signup` | — | Create an account |
| `POST` | `/auth/login` | — | Exchange credentials for a JWT |
| `GET` | `/auth/me` | ✅ | Current user |
| `POST` | `/comparisons` | ✅ | Save a matchup |
| `GET` | `/comparisons` | ✅ | List the current user's saved matchups |
| `DELETE` | `/comparisons/{id}` | ✅ | Delete one (403 if not the owner) |

Interactive docs are available at `/docs` when the server is running.

`/predict` returns `422` if the two fighters are the same or are in different weight
classes, since the model's input distribution assumes same-division matchups.

---

## Running locally

**Prerequisites:** Python 3.13, Node 20.19+ or 22+, PostgreSQL (Docker Desktop or a local install)

### Dataset

The fight data comes from the Ultimate UFC Dataset on Kaggle. Its terms don't allow
redistribution, so the CSV is **not in this repo** (`*.csv` is gitignored). Download
`ufc-master.csv` from Kaggle and place it at:

```
backend/data/ufc-master.csv
```

The seed script and `project.py` read it from there. The trained model
(`backend/ml/ufc_ml.pkl`) is committed, so the API itself runs without the CSV once
the database is seeded.

### Backend

```bash
cd backend
cp .env.example .env
```

Generate a real secret and put it in `.env` as `JWT_SECRET` — the app refuses to
start with the placeholder value:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Then:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt   # Windows
docker compose up -d                                          # Postgres on :5432
.venv/Scripts/python.exe -m alembic upgrade head              # create tables
.venv/Scripts/python.exe -m app.scripts.seed_fighters         # load 2,112 fighters
.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local     # VITE_API_URL=http://localhost:8000
npm install
npm run dev                    # http://localhost:5173
```

### Tests

```bash
cd backend
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m pytest
```

The tests use an in-memory SQLite database, so Postgres does not need to be running.
CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs them on every push,
along with `npm run lint` and `npm run build` for the frontend.

> On Windows PowerShell, run each command on its own line — `&&` chaining is not
> supported.

---

## Project structure

```
backend/
  app/
    main.py                     FastAPI app, CORS, router mounting
    core/       config.py       settings + startup security validation
                security.py     password hashing, JWT encode/decode
    db/         models.py       Fighter, User, SavedComparison
                session.py      engine, session factory, get_db dependency
    schemas/                    Pydantic request/response contracts
    api/        deps.py         get_db, get_current_user
                routes/         predict, fighters, auth, comparisons
    services/   model_service.py       loads the pickle, builds feature vectors
                prediction_service.py  validation shared by /predict and /comparisons
    scripts/    seed_fighters.py       CSV -> fighters table
  alembic/                      schema migrations
  tests/                        pytest suite (auth, predict, fighters, comparisons, seed)
  ml/ufc_ml.pkl                 trained model pipeline
frontend/
  src/
    api/                        axios client + endpoint modules
    context/AuthContext.jsx     auth state, token lifecycle
    components/                 FighterCard, FighterSelect, Spinner, ProtectedRoute
    pages/                      FighterList, FighterDetail, Comparison, Login, Signup, SavedComparisons
legacy/                         original Streamlit prototype and its model (superseded)
project.py                      model training script -> backend/ml/ufc_ml.pkl
.github/workflows/ci.yml        tests, lint, build
render.yaml                     Render blueprint (API + Postgres)
```

---

## Engineering notes

**Precomputed fighter profiles.** The original prototype re-read and re-aggregated
the full CSV on every prediction. Moving that work into a one-time seed step turned
each prediction into two indexed primary-key lookups.

**A silent data bug in the prototype.** The original aggregation built columns named
`TempOdds` but looked them up as `Temp_Odds`. The lookup never matched, so it always
fell through to a default that averaged the raw column across every fight a fighter
appeared in — quietly blending opponents' stats into each fighter's averages for
anyone who had fought from both corners. The rewrite computes each fighter's own
stats. The bug is preserved in [`legacy/`](legacy/) with an explanation, so that
directory remains an accurate record of the original.

**Fail-fast on an insecure JWT secret.** `JWT_SECRET` previously fell back to a
placeholder committed in `.env.example`. Because a JWT's signature is the only proof
of authenticity, a publicly known secret means anyone can mint a valid token for any
account. The app now validates the secret at startup and refuses to boot on the
placeholder or anything under 32 characters.

**Expired-token handling.** Tokens expire after 60 minutes. Without explicit
handling the UI kept showing a logged-in state while every request failed. An axios
response interceptor now clears the session on a `401` — while ignoring `401`s from
the login endpoint itself, where it simply means a wrong password.

**Server-side prediction on save.** `POST /comparisons` re-runs the prediction on the
server rather than trusting a result supplied by the client, sharing one validated
code path with `/predict`.

**Order-independent predictions.** Corner assignment used to be alphabetical, so
swapping two names could flip the predicted winner. Predictions are now averaged
over both corner assignments (see [Corner assignment](#corner-assignment)), and a
test pins that behaviour.

**Pinned dependencies.** With unpinned requirements, a fresh install picked up
SQLAlchemy 2.1, which uses the psycopg 3 driver for `postgresql://` URLs, while the
project shipped psycopg2. The deploy would have crashed on startup. The project now
uses psycopg 3, pins the driver in the database URL explicitly, and pins every
backend dependency.

---

## Deployment

The backend deploys to Render via the [`render.yaml`](render.yaml) blueprint, which
provisions the web service and PostgreSQL together, generates `JWT_SECRET`, and runs
migrations on every start. The frontend deploys to Vercel with root directory
`frontend` and `VITE_API_URL` pointed at the API.

**Seeding the deployed database.** The CSV isn't in the repo, so the server can't
seed itself; on startup the seed step logs a warning and the API starts with an empty
fighters table. Seed it once from your machine, where the CSV is. Copy the
database's **External Database URL** from the Render dashboard and run, from
`backend/`:

```powershell
$env:DATABASE_URL = "<External Database URL from Render>"
.venv\Scripts\python.exe -m app.scripts.seed_fighters
Remove-Item Env:DATABASE_URL
```

Only fighter profiles derived from the dataset are stored in the database; the raw
CSV is never uploaded.

After the frontend URL exists, set `CORS_ORIGINS` on the backend to that URL —
otherwise the browser blocks every request. [`frontend/vercel.json`](frontend/vercel.json)
contains the SPA rewrite rule so that deep links like `/compare` resolve on refresh
rather than 404ing.

Existing deployments pick up schema changes automatically: the start command runs
`alembic upgrade head`. New fighter columns are filled by re-running the seed from
your machine as above; it re-seeds any table where fighters are missing their UFC
record.

---

## Possible next steps

- Train on fighter stats as of each fight date, with a time-based train/test split,
  instead of a random split over 2010–2024 fights
- Add striking and grappling features (significant strikes, takedowns) that are in
  the dataset but not used yet
- Move the auth token from `localStorage` to an httpOnly cookie
