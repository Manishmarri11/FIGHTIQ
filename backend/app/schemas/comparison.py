from datetime import datetime

from pydantic import BaseModel


class SavedComparisonCreate(BaseModel):
    fighter1_id: int
    fighter2_id: int


class SavedComparisonOut(BaseModel):
    id: int
    fighter1_id: int
    fighter2_id: int
    fighter1_name: str
    fighter2_name: str
    predicted_winner_id: int
    predicted_winner_name: str
    fighter1_win_probability: float
    fighter2_win_probability: float
    created_at: datetime
