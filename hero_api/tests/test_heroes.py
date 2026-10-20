import pytest

BASE = "/api/v1/heroes"

def create(client, **overrides):
    payload = {"name": "Deadpond", "secret_name": "Dive Wilson", **overrides}
    return client.post(BASE, json=payload)

def test_list_empty(client):
    assert client.get(BASE).json() == []

def test_create_201_and_private_field_hidden(client):
    res = create(client)
    assert res.status_code == 201
    assert res.json()["status"] == "active"
    assert "secret_name" not in res.json()
    assert "created_at" in res.json()

def test_detail_200(client):
    hero_id = create(client).json()["id"]
    assert client.get(f"{BASE}/{hero_id}").json()["name"] == "Deadpond"

def test_detail_404(client):
    r = client.get(f"{BASE}/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Hero not found"}

@pytest.mark.parametrize("body", [
    {}, {"name": "X"}, {"name": "X", "secret_name": "Y", "age": -5},
    {"name": "X", "secret_name": "Y", "age": "old"},
    {"name": "X", "secret_name": "Y", "status": "dead"},
    {"name": "", "secret_name": "Y"},
])
def test_invalid_422(client, body):
    assert client.post(BASE, json=body).status_code == 422

def test_unknown_team_400(client):
    assert create(client, team_id=999).status_code == 400

def test_patch_only_supplied_field(client):
    hero_id = create(client, age=45).json()["id"]
    r = client.patch(f"{BASE}/{hero_id}", json={"status": "retired"})
    assert r.status_code == 200
    assert r.json()["age"] == 45
    assert r.json()["status"] == "retired"

def test_patch_null_name_422(client):
    hero_id = create(client).json()["id"]
    assert client.patch(f"{BASE}/{hero_id}", json={"name": None}).status_code == 422

def test_patch_unknown_team_400(client):
    hero_id = create(client).json()["id"]
    assert client.patch(f"{BASE}/{hero_id}", json={"team_id": 999}).status_code == 400

def test_delete_204_then_404(client):
    hero_id = create(client).json()["id"]
    r = client.delete(f"{BASE}/{hero_id}")
    assert r.status_code == 204 and not r.content
    assert client.get(f"{BASE}/{hero_id}").status_code == 404

def test_query_validation_422(client):
    assert client.get(f"{BASE}?limit=-1").status_code == 422
    assert client.get(f"{BASE}?limit=101").status_code == 422

def test_pagination_and_team_filter(client):
    team = client.post("/api/v1/teams", json={"name": "A", "headquarters": "NY"}).json()
    create(client, name="Hero 1", team_id=team["id"])
    create(client, name="Hero 2")
    create(client, name="Hero 3", team_id=team["id"])
    assert len(client.get(f"{BASE}?team_id={team['id']}").json()) == 2
    assert len(client.get(f"{BASE}?offset=1&limit=1").json()) == 1
