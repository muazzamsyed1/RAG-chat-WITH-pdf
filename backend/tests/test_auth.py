import pytest

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"

USER = {
    "email": "auth_test@example.com",
    "password": "TestPass1",
    "full_name": "Auth Test",
}


@pytest.mark.asyncio
async def test_register_success(client):
    r = await client.post(REGISTER, json=USER)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == USER["email"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post(REGISTER, json={**USER, "email": "dup@example.com"})
    r = await client.post(REGISTER, json={**USER, "email": "dup@example.com"})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client):
    r = await client.post(
        REGISTER, json={"email": "weak@example.com", "password": "abc"}
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(REGISTER, json={**USER, "email": "login_ok@example.com"})
    r = await client.post(
        LOGIN, json={"email": "login_ok@example.com", "password": "TestPass1"}
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(REGISTER, json={**USER, "email": "wrong_pw@example.com"})
    r = await client.post(
        LOGIN, json={"email": "wrong_pw@example.com", "password": "WrongPass9"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client):
    await client.post(REGISTER, json={**USER, "email": "me_test@example.com"})
    lr = await client.post(
        LOGIN, json={"email": "me_test@example.com", "password": "TestPass1"}
    )
    token = lr.json()["access_token"]
    r = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    assert r.json()["email"] == "me_test@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client):
    r = await client.get("/api/v1/users/me")
    assert r.status_code in (401, 403)
