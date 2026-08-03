from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Fighter
from app.schemas.fighter import FighterListResponse, FighterOut

router = APIRouter()


@router.get("/fighters", response_model=FighterListResponse)
def list_fighters(
    search: str | None = Query(None, description="Case-insensitive substring match on fighter name"),
    weight_class: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> FighterListResponse:
    stmt = select(Fighter)
    if search:
        stmt = stmt.where(Fighter.name.ilike(f"%{search}%"))
    if weight_class:
        stmt = stmt.where(Fighter.weight_class == weight_class)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))

    stmt = stmt.order_by(Fighter.name).offset((page - 1) * page_size).limit(page_size)
    fighters = db.scalars(stmt).all()

    return FighterListResponse(total=total or 0, page=page, page_size=page_size, fighters=fighters)


@router.get("/fighters/{fighter_id}", response_model=FighterOut)
def get_fighter(fighter_id: int, db: Session = Depends(get_db)) -> Fighter:
    fighter = db.get(Fighter, fighter_id)
    if fighter is None:
        raise HTTPException(status_code=404, detail=f"Fighter {fighter_id} not found")
    return fighter
