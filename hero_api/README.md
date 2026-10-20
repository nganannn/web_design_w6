# Week 10 — Heroes API (Lab 1, Lab 2, Lab 3)

Completed independently from the Week 10 slides. This is a standalone example, not a patch to your original Week 9 project.

## 1. Install

```bash
python -m pip install -r requirements.txt
```

## 2. Run the backend

```bash
python -m uvicorn app.main:app --reload
```

Open:
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- JSON schema: http://127.0.0.1:8000/openapi.json

The SQLite file `app.db` is initialized on server startup. To add sample data to a **new/empty** database, run `python -m app.seed`. Do **not** rerun the seed script on a populated database: team names must be unique.

## 3. Run the frontend

Run Live Server on `frontend/index.html` on `http://127.0.0.1:5500` (or `http://localhost:5500`). Alternatively:

```bash
python -m http.server 5500 --directory frontend
```

Open http://127.0.0.1:5500. The API must also be running on 8000. To reproduce the CORS error, temporarily remove `http://127.0.0.1:5500` from `allow_origins` in `app/main.py`, restart the backend, refresh the frontend, and restore it.

## 4. Test

```bash
python -m pytest -v
```

Tests use a **separate SQLite in-memory DB** (not `app.db`). Test coverage: 200, 201, 204, 400, 404, 409, 422; pagination, JSON validation, private output field, partial updates, team filters and nested resources.

## REST transformations (Lab 1)

| Old RPC route | New REST route |
|---|---|
| GET /getHeroes | GET /api/v1/heroes |
| GET /heroById?id=3 | GET /api/v1/heroes/3 |
| POST /addTeam | POST /api/v1/teams |
| POST /removeHero/3 | DELETE /api/v1/heroes/3 |
| GET /heroesOfTeam?team=1 | GET /api/v1/teams/1/heroes |
| POST /changeHeroTeam?hero=3&team=2 | PATCH /api/v1/heroes/3 with JSON `{ "team_id": 2 }` |

The frontend uses `textContent` to avoid HTML injection. Schema changes to an existing local `app.db` require migrations or recreating the database in development; `create_all()` does not update existing columns.
