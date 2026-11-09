from jose import jwt


def test_signup_then_login_returns_token(client):
    response = client.post("/auth/signup", json={"email": "Fan@Example.com", "password": "correct-horse"})
    assert response.status_code == 201
    assert response.json()["email"] == "fan@example.com"

    response = client.post("/auth/login", data={"username": "fan@example.com", "password": "correct-horse"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_signup_rejects_duplicate_email_case_insensitively(client):
    client.post("/auth/signup", json={"email": "fan@example.com", "password": "correct-horse"})
    response = client.post("/auth/signup", json={"email": "FAN@example.com", "password": "correct-horse"})
    assert response.status_code == 409


def test_signup_rejects_short_password(client):
    response = client.post("/auth/signup", json={"email": "fan@example.com", "password": "short"})
    assert response.status_code == 422


def test_login_wrong_password_and_unknown_email_look_the_same(client):
    client.post("/auth/signup", json={"email": "fan@example.com", "password": "correct-horse"})
    wrong_password = client.post("/auth/login", data={"username": "fan@example.com", "password": "nope-nope"})
    unknown_email = client.post("/auth/login", data={"username": "who@example.com", "password": "nope-nope"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_me_requires_valid_token(client, auth_headers):
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401

    response = client.get("/auth/me", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["email"] == "fan@example.com"


def test_token_signed_with_another_secret_is_rejected(client, auth_headers):
    auth_headers()  # create user id 1
    forged = jwt.encode({"sub": "1"}, "attacker-secret", algorithm="HS256")
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401
