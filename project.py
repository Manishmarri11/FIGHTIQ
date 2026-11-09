"""Train the fight outcome model and write it to backend/ml/ufc_ml.pkl.

The model is a single sklearn Pipeline (mean imputation -> standard scaling ->
logistic regression) fit on a DataFrame, so the saved pickle carries its own
preprocessing and feature names. The API passes raw fighter stats, with missing
values as NaN, and the pipeline handles the rest.

Also trains a variant without the betting-odds features, to show how much of the
accuracy comes from the market rather than from fighter attributes. Only the full
model is saved.

Run from the repo root: python project.py
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "backend" / "data" / "ufc-master.csv"
MODEL_PATH = ROOT / "backend" / "ml" / "ufc_ml.pkl"

# Order must match IMP_COLUMNS in backend/app/services/model_service.py.
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
ODDS_COLUMNS = ["RedOdds", "BlueOdds", "RedExpectedValue", "BlueExpectedValue"]
NO_ODDS_COLUMNS = [c for c in IMP_COLUMNS if c not in ODDS_COLUMNS]


def build_model():
    return make_pipeline(
        SimpleImputer(strategy="mean"),
        StandardScaler(),
        LogisticRegression(random_state=1),
    )


def evaluate(name, model, val_X, val_y):
    predictions = model.predict(val_X)
    scores = {
        "accuracy": accuracy_score(val_y, predictions),
        "f1": f1_score(val_y, predictions),
        "precision": precision_score(val_y, predictions, zero_division=0),
        "roc_auc": roc_auc_score(val_y, model.predict_proba(val_X)[:, 1]),
    }
    print(f"{name:<24}" + "  ".join(f"{k} {v:.3f}" for k, v in scores.items()))
    return scores


def main():
    data = pd.read_csv(CSV_PATH)
    y = data["Winner"].map({"Red": 1, "Blue": 0})
    X = data[IMP_COLUMNS]
    train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)

    baseline = DummyClassifier(strategy="most_frequent").fit(train_X, train_y)
    evaluate("Always pick Red", baseline, val_X, val_y)

    no_odds = build_model().fit(train_X[NO_ODDS_COLUMNS], train_y)
    evaluate("Without betting odds", no_odds, val_X[NO_ODDS_COLUMNS], val_y)

    model = build_model().fit(train_X, train_y)
    evaluate("Full model", model, val_X, val_y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"Saved model to {MODEL_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
