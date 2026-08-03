from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Fighter
from app.services.model_service import PredictionResult, model_service


def get_fighter_or_404(db: Session, fighter_id: int) -> Fighter:
    fighter = db.get(Fighter, fighter_id)
    if fighter is None:
        raise HTTPException(status_code=404, detail=f"Fighter {fighter_id} not found")
    return fighter


def run_prediction(db: Session, fighter1_id: int, fighter2_id: int) -> tuple[Fighter, Fighter, PredictionResult]:
    if fighter1_id == fighter2_id:
        raise HTTPException(status_code=422, detail="Select two different fighters")

    fighter1 = get_fighter_or_404(db, fighter1_id)
    fighter2 = get_fighter_or_404(db, fighter2_id)

    if fighter1.weight_class != fighter2.weight_class:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Fighters must be in the same weight class: "
                f"{fighter1.name} is {fighter1.weight_class}, "
                f"{fighter2.name} is {fighter2.weight_class}"
            ),
        )

    result = model_service.predict(fighter1, fighter2)
    return fighter1, fighter2, result


def fighter_probabilities(fighter1: Fighter, fighter2: Fighter, result: PredictionResult) -> tuple[float, float]:
    fighter1_prob = (
        result.red_win_probability if result.red_fighter.id == fighter1.id else result.blue_win_probability
    )
    fighter2_prob = (
        result.red_win_probability if result.red_fighter.id == fighter2.id else result.blue_win_probability
    )
    return fighter1_prob, fighter2_prob
