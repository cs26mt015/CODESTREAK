def registration_payload(**changes):
    payload = {
        "name": "  Casey Learner  ",
        "email": "casey@example.com",
        "password": "A-long-password-123!",
        "timezone": "Asia/Kolkata",
        "consent_status": "accepted",
    }
    payload.update(changes)
    return payload


def test_register_login_and_get_profile(client):
    created = client.post("/api/v1/auth/register", json=registration_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["user"]["name"] == "Casey Learner"
    assert body["user"]["role"] == "learner"
    assert body["user"]["email"] == "casey@example.com"
    assert body["access_token"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "CASEY@example.com", "password": "A-long-password-123!"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["user_id"] == body["user"]["user_id"]

    profile = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert profile.status_code == 200
    assert profile.json()["timezone"] == "Asia/Kolkata"
    assert "password_hash" not in profile.json()


def test_register_rejects_duplicate_unknown_timezone_and_invalid_fields(client):
    assert client.post("/api/v1/auth/register", json=registration_payload()).status_code == 201
    duplicate = client.post(
        "/api/v1/auth/register",
        json=registration_payload(email="CASEY@example.com"),
    )
    assert duplicate.status_code == 409

    unknown_timezone = client.post(
        "/api/v1/auth/register",
        json=registration_payload(email="other@example.com", timezone="Mars/Olympus"),
    )
    assert unknown_timezone.status_code == 422
    invalid = client.post(
        "/api/v1/auth/register",
        json=registration_payload(email="not-an-email", password="short"),
    )
    assert invalid.status_code == 422
    blank_name = client.post(
        "/api/v1/auth/register",
        json=registration_payload(email="blank@example.com", name="  "),
    )
    assert blank_name.status_code == 422


def test_login_rejects_unknown_user_and_wrong_password(client, make_user):
    make_user(email="known@example.com")
    missing = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "not-the-password"},
    )
    wrong = client.post(
        "/api/v1/auth/login",
        json={"email": "known@example.com", "password": "not-the-password"},
    )
    assert missing.status_code == wrong.status_code == 401
    assert missing.headers["www-authenticate"] == "Bearer"


def test_profile_update_validation_conflict_and_success(client, make_user, auth_headers):
    user = make_user(email="one@example.com")
    make_user(email="two@example.com")
    headers = auth_headers(user)

    assert client.patch("/api/v1/auth/me", json={}, headers=headers).status_code == 422
    assert client.patch("/api/v1/auth/me", json={"name": "  "}, headers=headers).status_code == 422
    assert client.patch(
        "/api/v1/auth/me", json={"email": "two@example.com"}, headers=headers
    ).status_code == 409
    assert client.patch(
        "/api/v1/auth/me", json={"timezone": "Not/AZone"}, headers=headers
    ).status_code == 422

    updated = client.patch(
        "/api/v1/auth/me",
        json={"name": "  Updated Name  ", "email": "NEW@example.com", "timezone": "UTC"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Name"
    assert updated.json()["email"] == "new@example.com"


def test_authentication_rejects_missing_invalid_and_deleted_user(client, make_user, auth_headers, db_session):
    assert client.get("/api/v1/auth/me").status_code == 401
    user = make_user()
    headers = auth_headers(user)
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer broken"}).status_code == 401
    db_session.delete(user)
    db_session.commit()
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401


def test_delete_profile_returns_no_content(client, make_user, auth_headers):
    user = make_user()
    response = client.delete("/api/v1/auth/me", headers=auth_headers(user))
    assert response.status_code == 204
    assert response.content == b""
