BASE = "/api/v1/teams"
BODY = {"name": "Avengers", "headquarters": "New York"}

def test_list_empty(client):
    assert client.get(BASE).json() == []

def test_create_team_201(client):
    r = client.post(BASE, json=BODY)
    assert r.status_code == 201
    assert r.json()["name"] == "Avengers"

def test_duplicate_team_409(client):
    assert client.post(BASE, json=BODY).status_code == 201
    r = client.post(BASE, json=BODY)
    assert r.status_code == 409
    assert r.json()["detail"] == "Team name already exists"

def test_nested_200(client):
    team_id = client.post(BASE, json=BODY).json()["id"]
    client.post("/api/v1/heroes", json={"name": "Tony", "secret_name": "Iron Man", "team_id": team_id})
    r = client.get(f"{BASE}/{team_id}/heroes")
    assert r.status_code == 200
    assert [h["name"] for h in r.json()] == ["Tony"]

def test_nested_404(client):
    assert client.get(f"{BASE}/999/heroes").status_code == 404

def test_bad_team_422(client):
    assert client.post(BASE, json={"name": "", "headquarters": "New York"}).status_code == 422
