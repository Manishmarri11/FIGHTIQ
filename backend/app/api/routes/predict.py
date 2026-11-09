from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.predict import PredictRequest, PredictResponse
from app.services.prediction_service import run_prediction

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db)) -> PredictResponse:
    fighter1, fighter2, result = run_prediction(db, request.fighter1_id, request.fighter2_id)

    return PredictResponse(
        fighter1_id=fighter1.id,
        fighter2_id=fighter2.id,
        winner_id=result.winner.id,
        winner_name=result.winner.name,
        fighter1_win_probability=result.fighter1_win_probability,
        fighter2_win_probability=result.fighter2_win_probability,
    )
