from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import SavedComparison, User
from app.schemas.comparison import SavedComparisonCreate, SavedComparisonOut
from app.services.prediction_service import fighter_probabilities, run_prediction

router = APIRouter(prefix="/comparisons")


def _to_out(comparison: SavedComparison) -> SavedComparisonOut:
    return SavedComparisonOut(
        id=comparison.id,
        fighter1_id=comparison.fighter1_id,
        fighter2_id=comparison.fighter2_id,
        fighter1_name=comparison.fighter1.name,
        fighter2_name=comparison.fighter2.name,
        predicted_winner_id=comparison.predicted_winner_id,
        predicted_winner_name=comparison.predicted_winner.name,
        fighter1_win_probability=comparison.fighter1_win_probability,
        fighter2_win_probability=comparison.fighter2_win_probability,
        created_at=comparison.created_at,
    )


@router.post("", response_model=SavedComparisonOut, status_code=status.HTTP_201_CREATED)
def create_comparison(
    request: SavedComparisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedComparisonOut:
    fighter1, fighter2, result = run_prediction(db, request.fighter1_id, request.fighter2_id)
    fighter1_prob, fighter2_prob = fighter_probabilities(fighter1, fighter2, result)

    comparison = SavedComparison(
        user_id=current_user.id,
        fighter1_id=fighter1.id,
        fighter2_id=fighter2.id,
        predicted_winner_id=result.winner.id,
        fighter1_win_probability=fighter1_prob,
        fighter2_win_probability=fighter2_prob,
    )
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    return _to_out(comparison)


@router.get("", response_model=list[SavedComparisonOut])
def list_comparisons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedComparisonOut]:
    comparisons = db.scalars(
        select(SavedComparison)
        .where(SavedComparison.user_id == current_user.id)
        .order_by(SavedComparison.created_at.desc())
    ).all()
    return [_to_out(c) for c in comparisons]


@router.delete("/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comparison(
    comparison_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    comparison = db.get(SavedComparison, comparison_id)
    if comparison is None:
        raise HTTPException(status_code=404, detail=f"Saved comparison {comparison_id} not found")
    if comparison.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comparison")

    db.delete(comparison)
    db.commit()
