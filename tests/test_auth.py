
def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "is_active" in data


def test_login_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "123456",
        },
    )

    assert register_response.status_code == 200

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "123456",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client):
    client.post(
        "/auth/register",
        json={
            "name": "Me User",
            "email": "me@example.com",
            "password": "123456",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "123456",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Me User"
    assert data["email"] == "me@example.com"


def test_register_duplicate_email(client):
    user_data = {
        "name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "123456",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert second_response.status_code == 400
    assert second_response.json()["message"] == "Email already registered"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Wrong Password User",
            "email": "wrong@example.com",
            "password": "123456",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Incorrect password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "notfound@example.com",
            "password": "123456",
        },
    )

    assert response.status_code == 401
    assert response.json()["message"] == "User does not exist"


def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_current_user_with_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401

