# Legacy — original Streamlit prototype

`app.py` is the first version of this project: a single-file Streamlit app that
loaded the pickled model and computed predictions directly from the CSV on every
interaction.

It is kept for reference only. The current application is:

- **Backend** — FastAPI + PostgreSQL (`../backend`)
- **Frontend** — React + Vite (`../frontend`)

## Known bug in this version

This prototype has a defect that was found and fixed during the rewrite.

When averaging a fighter's historical stats, it renames the opponent's columns to
a `Temp`-prefixed form, then looks them up with an extra underscore:

```python
input_row[col] = red_avg_stats.get('Temp_' + stat, red_avg_stats.get(col, 0))
#                                       ^ key is actually "TempOdds", not "Temp_Odds"
```

That lookup never matches, so it always silently falls through to the second
argument — averaging the raw `Red*`/`Blue*` column across every fight the fighter
appears in. For any fighter who has fought from both corners, that mixes their
opponents' stats into their own averages.

The rewrite computes each fighter's own stats correctly. See
`../backend/app/scripts/seed_fighters.py`.

The bug is deliberately left in place here so this file remains an accurate record
of the original version.

## Running it

```bash
pip install streamlit pandas scikit-learn
cd legacy
streamlit run app.py
```

Paths are relative to this directory, so it must be run from inside `legacy/`. It
reads the dataset from `../backend/data/ufc-master.csv`, which is not in the repo;
see "Dataset" in the main README.

`ufc_ml.pkl` here is the original model (a bare logistic regression without
scaling) that this prototype was built against. The current API uses a retrained
pipeline in `../backend/ml/`, which expects different input handling.
