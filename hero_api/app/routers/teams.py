from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from app.database import SessionDep
from app.models import Hero, HeroPublic, Team, TeamCreate, TeamPublic

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamPublic], summary="List teams")
def list_teams(session: SessionDep):
    """Return all available teams."""
    return session.exec(select(Team).order_by(Team.id)).all()


@router.post("", response_model=TeamPublic, status_code=status.HTTP_201_CREATED,
             summary="Create a team", responses={409: {"description": "Team name already exists"}})
def create_team(team_in: TeamCreate, session: SessionDep):
    """Create a team; duplicate names return HTTP 409."""
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists") from None
    session.refresh(team)
    return team


@router.get("/{team_id}/heroes", response_model=list[HeroPublic],
            summary="List the heroes of a team", responses={404: {"description": "Team not found"}})
def list_team_heroes(team_id: int, session: SessionDep):
    """Return heroes belonging to an existing team."""
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return session.exec(select(Hero).where(Hero.team_id == team_id).order_by(Hero.id)).all()
