from datetime import datetime, timezone
from enum import Enum
from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HeroStatus(str, Enum):
    active = "active"
    retired = "retired"


class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True, min_length=1, max_length=50, schema_extra={"examples": ["Avengers"]})
    headquarters: str = Field(schema_extra={"examples": ["New York"]})


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: int


class HeroBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=50, schema_extra={"examples": ["Deadpond"]})
    age: int | None = Field(default=None, ge=0, le=1000, schema_extra={"examples": [30]})
    status: HeroStatus = HeroStatus.active
    team_id: int | None = Field(default=None, foreign_key="team.id")


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str
    created_at: datetime = Field(default_factory=utc_now)
    team: Team | None = Relationship(back_populates="heroes")


class HeroCreate(HeroBase):
    secret_name: str = Field(min_length=1, schema_extra={"examples": ["Dive Wilson"]})


class HeroPublic(HeroBase):
    id: int
    created_at: datetime


class HeroUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    age: int | None = Field(default=None, ge=0, le=1000)
    status: HeroStatus | None = None
    team_id: int | None = None

    @field_validator("name", "status")
    @classmethod
    def not_null(cls, value):
        if value is None:
            raise ValueError("cannot be null")
        return value
