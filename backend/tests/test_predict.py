import pytest


def predict(client, fighter1_id, fighter2_id):
    return client.post("/predict", json={"fighter1_id": fighter1_id, "fighter2_id": fighter2_id})


def test_predict_returns_probabilities_that_sum_to_one(client, fighters):
    favourite, underdog, _ = fighters
    response = predict(client, favourite.id, underdog.id)
    assert response.status_code == 200
    body = response.json()
    assert body["fighter1_win_probability"] + body["fighter2_win_probability"] == pytest.approx(1)
    assert body["winner_id"] == favourite.id


def test_predict_does_not_depend_on_argument_order(client, fighters):
    favourite, underdog, _ = fighters
    forward = predict(client, favourite.id, underdog.id).json()
    reverse = predict(client, underdog.id, favourite.id).json()
    assert forward["winner_id"] == reverse["winner_id"]
    assert forward["fighter1_win_probability"] == pytest.approx(reverse["fighter2_win_probability"])


def test_predict_handles_missing_stats(client, db_session, fighters):
    favourite, underdog, _ = fighters
    underdog.reach_cms = None
    underdog.avg_odds = None
    db_session.commit()
    assert predict(client, favourite.id, underdog.id).status_code == 200


def test_predict_rejects_same_fighter(client, fighters):
    favourite, _, _ = fighters
    assert predict(client, favourite.id, favourite.id).status_code == 422


def test_predict_rejects_different_weight_classes(client, fighters):
    favourite, _, heavyweight = fighters
    response = predict(client, favourite.id, heavyweight.id)
    assert response.status_code == 422
    assert "same weight class" in response.json()["detail"]


def test_predict_unknown_fighter_is_404(client, fighters):
    favourite, _, _ = fighters
    assert predict(client, favourite.id, 9999).status_code == 404
