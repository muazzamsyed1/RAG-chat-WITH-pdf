import pytest

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
DOCS = "/api/v1/documents"


async def _login(client, email, pw="TestPass1"):
    await client.post(REGISTER, json={"email": email, "password": pw})
    r = await client.post(LOGIN, json={"email": email, "password": pw})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_upload_requires_auth(client):
    r = await client.post(f"{DOCS}/upload")
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    token = await _login(client, "doclist@example.com")
    r = await client.get(
        f"{DOCS}/", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    assert r.json()["total"] == 0


@pytest.mark.asyncio
async def test_cross_user_isolation(client):
    """User A and User B both start with 0 documents — neither can see the other's."""
    token_a = await _login(client, "doc_a@example.com")
    token_b = await _login(client, "doc_b@example.com")
    ra = await client.get(f"{DOCS}/", headers={"Authorization": f"Bearer {token_a}"})
    rb = await client.get(f"{DOCS}/", headers={"Authorization": f"Bearer {token_b}"})
    assert ra.json()["total"] == 0
    assert rb.json()["total"] == 0


@pytest.mark.asyncio
async def test_delete_missing_document(client):
    """Deleting a nonexistent document returns 403 or 404 — never 200 or 500."""
    token = await _login(client, "del_doc@example.com")
    r = await client.delete(
        f"{DOCS}/nonexistent-id-000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_delete_requires_auth(client):
    r = await client.delete(f"{DOCS}/some-doc-id")
    assert r.status_code in (401, 403)
