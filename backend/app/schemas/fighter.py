from datetime import date

from pydantic import BaseModel, ConfigDict


class FighterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    weight_class: str | None
    gender: str | None
    stance: str | None
    height_cms: float | None
    reach_cms: float | None
    weight_lbs: float | None
    age: int | None
    current_win_streak: float | None
    current_lose_streak: float | None
    wins: float | None
    losses: float | None
    wins_by_ko: float | None
    wins_by_submission: float | None
    wins_by_decision_majority: float | None
    wins_by_decision_split: float | None
    wins_by_decision_unanimous: float | None
    avg_odds: float | None
    avg_expected_value: float | None
    total_fights: int | None
    last_fight_date: date | None


class FighterListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    fighters: list[FighterOut]
