import os

# Must be set before app modules are imported: config validates the secret at startup
# and session.py builds its engine from DATABASE_URL at import time.
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-validation"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import Fighter
from app.db.session import get_db
from app.main import app

# Realistic-looking stats; the model needs plausible inputs, not exact ones.
FIGHTER_STATS = dict(
    gender="MALE",
    stance="Orthodox",
    height_cms=185.0,
    reach_cms=190.0,
    weight_lbs=185.0,
    age=30,
    current_win_streak=2.0,
    current_lose_streak=0.0,
    wins=8.0,
    losses=2.0,
    wins_by_ko=3.0,
    wins_by_submission=2.0,
    wins_by_decision_majority=0.0,
    wins_by_decision_split=1.0,
    wins_by_decision_unanimous=2.0,
    avg_odds=-150.0,
    avg_expected_value=66.0,
    total_fights=10,
    ufc_wins=9,
    ufc_losses=2,
    ufc_draws=0,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def fighters(db_session):
    """Two middleweights who differ clearly, plus one heavyweight."""
    favourite = Fighter(name="Alpha Favourite", weight_class="Middleweight", **FIGHTER_STATS)
    underdog = Fighter(
        name="Zulu Underdog",
        weight_class="Middleweight",
        **{**FIGHTER_STATS, "avg_odds": 250.0, "avg_expected_value": 250.0, "wins": 2.0, "losses": 5.0},
    )
    heavyweight = Fighter(name="Heavy Hitter", weight_class="Heavyweight", **FIGHTER_STATS)
    db_session.add_all([favourite, underdog, heavyweight])
    db_session.commit()
    return favourite, underdog, heavyweight


@pytest.fixture
def auth_headers(client):
    def make(email="fan@example.com", password="correct-horse"):
        client.post("/auth/signup", json={"email": email, "password": password})
        token = client.post("/auth/login", data={"username": email, "password": password}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return make
