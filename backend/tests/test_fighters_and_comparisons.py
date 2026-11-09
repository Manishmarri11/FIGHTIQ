def test_list_fighters_filters_and_paginates(client, fighters):
    body = client.get("/fighters", params={"weight_class": "Middleweight"}).json()
    assert body["total"] == 2
    assert [f["name"] for f in body["fighters"]] == ["Alpha Favourite", "Zulu Underdog"]

    body = client.get("/fighters", params={"search": "heavy"}).json()
    assert [f["name"] for f in body["fighters"]] == ["Heavy Hitter"]

    body = client.get("/fighters", params={"page": 2, "page_size": 2}).json()
    assert body["total"] == 3
    assert len(body["fighters"]) == 1


def test_get_fighter_includes_ufc_record(client, fighters):
    favourite, _, _ = fighters
    body = client.get(f"/fighters/{favourite.id}").json()
    assert (body["ufc_wins"], body["ufc_losses"], body["ufc_draws"]) == (9, 2, 0)
    assert client.get("/fighters/9999").status_code == 404


def test_comparisons_require_login(client, fighters):
    favourite, underdog, _ = fighters
    assert client.get("/comparisons").status_code == 401
    response = client.post("/comparisons", json={"fighter1_id": favourite.id, "fighter2_id": underdog.id})
    assert response.status_code == 401


def test_save_list_and_delete_comparison(client, fighters, auth_headers):
    favourite, underdog, _ = fighters
    headers = auth_headers()

    created = client.post(
        "/comparisons", json={"fighter1_id": favourite.id, "fighter2_id": underdog.id}, headers=headers
    )
    assert created.status_code == 201
    saved = created.json()
    assert saved["predicted_winner_name"] == "Alpha Favourite"

    # The stored prediction matches what /predict returns for the same matchup.
    live = client.post("/predict", json={"fighter1_id": favourite.id, "fighter2_id": underdog.id}).json()
    assert saved["fighter1_win_probability"] == live["fighter1_win_probability"]

    assert [c["id"] for c in client.get("/comparisons", headers=headers).json()] == [saved["id"]]
    assert client.delete(f"/comparisons/{saved['id']}", headers=headers).status_code == 204
    assert client.get("/comparisons", headers=headers).json() == []


def test_users_cannot_see_or_delete_each_others_comparisons(client, fighters, auth_headers):
    favourite, underdog, _ = fighters
    owner = auth_headers("owner@example.com")
    other = auth_headers("other@example.com")

    saved = client.post(
        "/comparisons", json={"fighter1_id": favourite.id, "fighter2_id": underdog.id}, headers=owner
    ).json()

    assert client.get("/comparisons", headers=other).json() == []
    assert client.delete(f"/comparisons/{saved['id']}", headers=other).status_code == 403
