"""Loads the trained model (ml/ufc_ml.pkl) and serves predictions.

The model is an sklearn Pipeline (imputer -> scaler -> logistic regression) trained in
project.py on a DataFrame with IMP_COLUMNS, with Winner mapped to 1 = Red corner,
0 = Blue corner. Missing stats are passed as NaN so the pipeline's imputer fills them
the same way it did during training.

The model only knows "Red" and "Blue", and Red won 58% of the training fights, so
which fighter is placed in which corner shifts the output, sometimes enough to flip
the winner. A real matchup has no corner yet, so each prediction is run both ways and
averaged: P(A wins) = mean(P(Red wins | A is Red), P(Blue wins | A is Blue)). The
result is the same no matter which order the two fighters are given in.
"""

import math
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
    fighter1_win_probability: float
    fighter2_win_probability: float


class ModelService:
    def __init__(self, model_path: str):
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
        self._red_class_index = list(self.model.classes_).index(1)

    def _build_feature_row(self, red_fighter: Fighter, blue_fighter: Fighter) -> pd.DataFrame:
        row = {}
        for col in IMP_COLUMNS:
            if col.startswith("Red"):
                fighter, suffix = red_fighter, col[len("Red"):]
            else:
                fighter, suffix = blue_fighter, col[len("Blue"):]
            value = getattr(fighter, STAT_SUFFIX_TO_ATTR[suffix])
            row[col] = value if value is not None else math.nan
        return pd.DataFrame([row], columns=IMP_COLUMNS)

    def predict(self, fighter1: Fighter, fighter2: Fighter) -> PredictionResult:
        features = pd.concat(
            [self._build_feature_row(fighter1, fighter2), self._build_feature_row(fighter2, fighter1)],
            ignore_index=True,
        )
        red_win = self.model.predict_proba(features)[:, self._red_class_index]
        fighter1_prob = float((red_win[0] + (1 - red_win[1])) / 2)
        fighter2_prob = 1 - fighter1_prob

        # On an exact tie, pick the alphabetically first name so the winner stays
        # independent of argument order.
        if fighter1_prob == fighter2_prob:
            winner = min(fighter1, fighter2, key=lambda f: f.name)
        else:
            winner = fighter1 if fighter1_prob > fighter2_prob else fighter2
        return PredictionResult(
            winner=winner,
            fighter1_win_probability=fighter1_prob,
            fighter2_win_probability=fighter2_prob,
        )


model_service = ModelService(settings.model_path)
