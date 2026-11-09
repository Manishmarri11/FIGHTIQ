import pandas as pd
import pytest

from app.core.config import INSECURE_JWT_SECRET, Settings
from app.scripts.seed_fighters import STAT_COLUMNS, build_fighter_table


def fight(date, red, blue, winner, red_wins, blue_wins, red_reach=180.0, blue_reach=170.0):
    row = {"Date": date, "Winner": winner, "WeightClass": "Lightweight", "Gender": "MALE"}
    for corner, name, wins, reach in (("Red", red, red_wins, red_reach), ("Blue", blue, blue_wins, blue_reach)):
        row.update({f"{corner}{stat}": 0 for stat in STAT_COLUMNS})
        row.update(
            {
                f"{corner}Fighter": name,
                f"{corner}Stance": "Orthodox",
                f"{corner}Age": 30,
                f"{corner}Draws": 0,
                f"{corner}Wins": wins,
                f"{corner}Losses": 1,
                f"{corner}ReachCms": reach,
            }
        )
    return row


@pytest.fixture
def fighter_table(tmp_path):
    csv = tmp_path / "fights.csv"
    pd.DataFrame(
        [
            # Ann fights from Red, then from Blue; her stats must never mix with Bea's.
            fight("2020-01-01", "Ann", "Bea", "Red", red_wins=5, blue_wins=2, red_reach=180, blue_reach=170),
            fight("2021-01-01", "Bea", "Ann", "Red", red_wins=2, blue_wins=6, red_reach=170, blue_reach=182),
        ]
    ).to_csv(csv, index=False)
    return build_fighter_table(str(csv)).set_index("name")


def test_seed_averages_only_the_fighters_own_stats(fighter_table):
    assert fighter_table.loc["Ann", "reach_cms"] == 181
    assert fighter_table.loc["Bea", "reach_cms"] == 170
    assert fighter_table.loc["Ann", "total_fights"] == 2


def test_seed_record_includes_result_of_last_fight(fighter_table):
    # Ann went into her last fight at 6-1 and lost it; Bea went in at 2-1 and won.
    assert (fighter_table.loc["Ann", "ufc_wins"], fighter_table.loc["Ann", "ufc_losses"]) == (6, 2)
    assert (fighter_table.loc["Bea", "ufc_wins"], fighter_table.loc["Bea", "ufc_losses"]) == (3, 1)


@pytest.mark.parametrize(
    "url, expected",
    [
        ("postgresql://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("sqlite://", "sqlite://"),
    ],
)
def test_database_url_pins_psycopg_driver(url, expected):
    assert Settings(database_url=url).sqlalchemy_database_url == expected


@pytest.mark.parametrize("secret", [INSECURE_JWT_SECRET, "too-short"])
def test_startup_rejects_weak_jwt_secret(secret):
    with pytest.raises(RuntimeError):
        Settings(jwt_secret=secret).validate_security()
