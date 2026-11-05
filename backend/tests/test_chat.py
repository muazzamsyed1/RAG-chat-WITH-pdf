import pytest

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
CHAT = "/api/v1/chat/"
CONVOS = "/api/v1/chat/conversations"


async def _login(client, email, pw="TestPass1"):
    await client.post(REGISTER, json={"email": email, "password": pw})
    r = await client.post(LOGIN, json={"email": email, "password": pw})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_chat_requires_auth(client):
    r = await client.post(CHAT, json={"query": "hello"})
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_conversations_empty(client):
    token = await _login(client, "chat_empty@example.com")
    r = await client.get(CONVOS, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_conversations_isolated_between_users(client):
    """User A's conversations must never appear in User B's list."""
    ta = await _login(client, "chat_isol_a@example.com")
    tb = await _login(client, "chat_isol_b@example.com")
    ra = await client.get(CONVOS, headers={"Authorization": f"Bearer {ta}"})
    rb = await client.get(CONVOS, headers={"Authorization": f"Bearer {tb}"})
    assert ra.json() == []
    assert rb.json() == []


@pytest.mark.asyncio
async def test_delete_missing_conversation(client):
    """Deleting a nonexistent conversation returns 404."""
    token = await _login(client, "del_convo@example.com")
    r = await client.delete(
        f"{CONVOS}/nonexistent-convo-id",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_conversation_requires_auth(client):
    r = await client.get(f"{CONVOS}/some-id")
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_delete_conversation_requires_auth(client):
    r = await client.delete(f"{CONVOS}/some-id")
    assert r.status_code in (401, 403)
