from pydantic import BaseModel


class PredictRequest(BaseModel):
    fighter1_id: int
    fighter2_id: int


class PredictResponse(BaseModel):
    fighter1_id: int
    fighter2_id: int
    winner_id: int
    winner_name: str
    fighter1_win_probability: float
    fighter2_win_probability: float
