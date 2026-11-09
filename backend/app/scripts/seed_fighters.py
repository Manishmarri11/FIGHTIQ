"""One-off script: aggregate ufc-master.csv into one row per fighter and upsert into Postgres.

Each CSV row is a single fight with RedFighter/BlueFighter stats recorded at fight time. This
script reshapes both corners into a long "one row per fighter-appearance" table, then averages
each fighter's own stats across every fight they appear in (regardless of which corner they
fought from), and takes their most recent fight for point-in-time attributes (weight class,
stance, age).

Note: legacy/app.py's in-app aggregation had a bug (a 'Temp_' vs 'Temp' key mismatch) that
silently disabled its cross-corner reassignment, so its "per-fighter average" actually mixed in
opponents' stats from fights where the fighter appeared in the other corner. This script fixes
that: stats below are the fighter's own values only.

Run with: python -m app.scripts.seed_fighters
"""

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.db.models import Fighter
from app.db.session import SessionLocal

STAT_COLUMNS = [
    "CurrentLoseStreak",
    "CurrentWinStreak",
    "Losses",
    "Wins",
    "WinsByDecisionMajority",
    "WinsByDecisionSplit",
    "WinsByDecisionUnanimous",
    "WinsByKO",
    "WinsBySubmission",
    "HeightCms",
    "ReachCms",
    "WeightLbs",
    "Odds",
    "ExpectedValue",
]

RENAME_TO_SCHEMA = {
    "Odds": "avg_odds",
    "ExpectedValue": "avg_expected_value",
    "CurrentLoseStreak": "current_lose_streak",
    "CurrentWinStreak": "current_win_streak",
    "Losses": "losses",
    "Wins": "wins",
    "WinsByDecisionMajority": "wins_by_decision_majority",
    "WinsByDecisionSplit": "wins_by_decision_split",
    "WinsByDecisionUnanimous": "wins_by_decision_unanimous",
    "WinsByKO": "wins_by_ko",
    "WinsBySubmission": "wins_by_submission",
    "HeightCms": "height_cms",
    "ReachCms": "reach_cms",
    "WeightLbs": "weight_lbs",
    "WeightClass": "weight_class",
    "Gender": "gender",
    "Date": "last_fight_date",
}


def _corner_long(df: pd.DataFrame, corner: str) -> pd.DataFrame:
    name_col = f"{corner}Fighter"
    stance_col = f"{corner}Stance"
    age_col = f"{corner}Age"
    stat_cols = [f"{corner}{stat}" for stat in STAT_COLUMNS]

    long_df = df[[name_col, "Date", "WeightClass", "Gender", stance_col, age_col, f"{corner}Draws"] + stat_cols].copy()
    long_df = long_df.rename(
        columns={
            name_col: "name",
            stance_col: "stance",
            age_col: "age",
            f"{corner}Draws": "draws",
            **{f"{corner}{stat}": stat for stat in STAT_COLUMNS},
        }
    )
    long_df["won"] = (df["Winner"] == corner).astype(int)
    return long_df


def _ufc_record(latest_rows: pd.DataFrame) -> pd.DataFrame:
    """The CSV's Wins/Losses/Draws are the fighter's record going *into* each fight, so
    the record after their most recent fight is those counts plus that fight's result."""
    return pd.DataFrame(
        {
            "ufc_wins": latest_rows["Wins"] + latest_rows["won"],
            "ufc_losses": latest_rows["Losses"] + (1 - latest_rows["won"]),
            "ufc_draws": latest_rows["draws"],
        }
    ).astype("Int64")


def build_fighter_table(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["Date"])

    long_df = pd.concat([_corner_long(df, "Red"), _corner_long(df, "Blue")], ignore_index=True)
    long_df = long_df.sort_values("Date", kind="stable")

    avg_stats = long_df.groupby("name")[STAT_COLUMNS].mean()
    total_fights = long_df.groupby("name").size().rename("total_fights")
    latest_rows = long_df.groupby("name").tail(1).set_index("name")
    latest = latest_rows[["WeightClass", "Gender", "stance", "age", "Date"]]

    fighters = avg_stats.join([total_fights, latest, _ufc_record(latest_rows)]).reset_index()
    fighters = fighters.rename(columns=RENAME_TO_SCHEMA)
    fighters["age"] = fighters["age"].astype("Int64")
    fighters["last_fight_date"] = fighters["last_fight_date"].dt.date
    fighters = fighters.astype(object).where(pd.notnull(fighters), None)
    return fighters


def upsert_fighters(fighters: pd.DataFrame) -> int:
    records = fighters.to_dict(orient="records")
    with SessionLocal() as session:
        stmt = insert(Fighter).values(records)
        update_cols = {c.name: c for c in stmt.excluded if c.name not in ("id", "name")}
        stmt = stmt.on_conflict_do_update(index_elements=["name"], set_=update_cols)
        session.execute(stmt)
        session.commit()
    return len(records)


def fighter_count() -> int:
    with SessionLocal() as session:
        return session.query(Fighter).count()


def missing_record_count() -> int:
    """Rows seeded before the ufc_* record columns existed."""
    with SessionLocal() as session:
        return session.query(Fighter).filter(Fighter.ufc_wins.is_(None)).count()


if __name__ == "__main__":
    # --force re-seeds even if the table is already populated. Without it the
    # script is a no-op on an already-seeded, up-to-date database, so it is safe
    # (and cheap) to run on every deploy/restart.
    force = "--force" in sys.argv
    existing = fighter_count()
    if existing and not force and not missing_record_count():
        print(f"Fighters table already has {existing} rows; skipping seed (use --force to re-seed).")
    elif not Path(settings.csv_path).is_file():
        # The dataset is not in the repo (Kaggle's terms don't allow republishing it), so a
        # fresh deploy has no CSV. Exit cleanly so the API still starts; seed this database
        # from a machine that has the file, by pointing DATABASE_URL at it (see README).
        print(
            f"WARNING: {settings.csv_path} not found; fighters table not seeded. "
            "Download the dataset and run this script with DATABASE_URL pointing at this database.",
            file=sys.stderr,
        )
    else:
        fighters = build_fighter_table(settings.csv_path)
        count = upsert_fighters(fighters)
        print(f"Seeded {count} fighters from {settings.csv_path}")
