"""Loads the existing trained model (ufc_ml.pkl) and serves predictions.

The model was trained in project.py on IMP_COLUMNS, in this exact order, with
Winner mapped to 1 = Red corner, 0 = Blue corner. Column order must match training
exactly since the model has no feature names attached (a bare sklearn Pipeline-less
LogisticRegression fit on a plain numpy array via SimpleImputer.fit_transform).

Corner assignment (which fighter is "Red" vs "Blue") is decided by sorting the two
fighter names alphabetically, matching legacy/app.py's original behavior.
"""

import pickle
from dataclasses import dataclass

import pandas as pd

from app.core.config import settings
from app.db.models import Fighter

IMP_COLUMNS = [
    "RedOdds", "BlueOdds", "RedExpectedValue", "BlueExpectedValue",
    "BlueCurrentLoseStreak", "BlueCurrentWinStreak", "BlueLosses",
    "BlueWinsByDecisionMajority", "BlueWinsByDecisionSplit", "BlueWinsByDecisionUnanimous",
    "BlueWinsByKO", "BlueWinsBySubmission", "BlueWins",
    "BlueHeightCms", "BlueReachCms", "BlueWeightLbs",
    "RedCurrentLoseStreak", "RedCurrentWinStreak", "RedLosses",
    "RedWinsByDecisionMajority", "RedWinsByDecisionSplit", "RedWinsByDecisionUnanimous",
    "RedWinsByKO", "RedWinsBySubmission", "RedWins",
    "RedHeightCms", "RedReachCms", "RedWeightLbs",
]

STAT_SUFFIX_TO_ATTR = {
    "Odds": "avg_odds",
    "ExpectedValue": "avg_expected_value",
    "CurrentLoseStreak": "current_lose_streak",
    "CurrentWinStreak": "current_win_streak",
    "Losses": "losses",
    "WinsByDecisionMajority": "wins_by_decision_majority",
    "WinsByDecisionSplit": "wins_by_decision_split",
    "WinsByDecisionUnanimous": "wins_by_decision_unanimous",
    "WinsByKO": "wins_by_ko",
    "WinsBySubmission": "wins_by_submission",
    "Wins": "wins",
    "HeightCms": "height_cms",
    "ReachCms": "reach_cms",
    "WeightLbs": "weight_lbs",
}


@dataclass
class PredictionResult:
    winner: Fighter
    red_fighter: Fighter
    blue_fighter: Fighter
    red_win_probability: float
    blue_win_probability: float


class ModelService:
    def __init__(self, model_path: str):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def _assign_corners(self, fighter_a: Fighter, fighter_b: Fighter) -> tuple[Fighter, Fighter]:
        by_name = {fighter_a.name: fighter_a, fighter_b.name: fighter_b}
        red_name, blue_name = sorted(by_name.keys())
        return by_name[red_name], by_name[blue_name]

    def _build_feature_row(self, red_fighter: Fighter, blue_fighter: Fighter) -> pd.DataFrame:
        row = {}
        for col in IMP_COLUMNS:
            if col.startswith("Red"):
                fighter, suffix = red_fighter, col[len("Red"):]
            else:
                fighter, suffix = blue_fighter, col[len("Blue"):]
            attr = STAT_SUFFIX_TO_ATTR[suffix]
            value = getattr(fighter, attr)
            row[col] = value if value is not None else 0
        return pd.DataFrame([row], columns=IMP_COLUMNS)

    def predict(self, fighter_a: Fighter, fighter_b: Fighter) -> PredictionResult:
        red_fighter, blue_fighter = self._assign_corners(fighter_a, fighter_b)
        features = self._build_feature_row(red_fighter, blue_fighter)

        predicted_class = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0]
        classes = list(self.model.classes_)
        red_prob = float(proba[classes.index(1)])
        blue_prob = float(proba[classes.index(0)])

        winner = red_fighter if predicted_class == 1 else blue_fighter
        return PredictionResult(
            winner=winner,
            red_fighter=red_fighter,
            blue_fighter=blue_fighter,
            red_win_probability=red_prob,
            blue_win_probability=blue_prob,
        )


model_service = ModelService(settings.model_path)
