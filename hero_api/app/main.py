from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.database import engine
from app.models import Hero, Team  # noqa: F401 -- register tables
from app.routers import heroes, teams

app = FastAPI(
    title="Heroes API", version="1.0.0",
    description="Week 10: REST, JSON, OpenAPI, CORS and pytest",
    openapi_tags=[
        {"name": "heroes", "description": "Create, read, update and delete heroes."},
        {"name": "teams", "description": "Manage teams and their heroes."},
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(heroes.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")

@app.on_event("startup")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
