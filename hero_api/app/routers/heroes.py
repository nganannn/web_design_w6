from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from app.database import SessionDep
from app.models import Hero, HeroCreate, HeroPublic, HeroUpdate, Team

router = APIRouter(prefix="/heroes", tags=["heroes"])
NOT_FOUND = {404: {"description": "Hero not found"}}


def get_hero_or_404(session, hero_id: int) -> Hero:
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


def check_team_exists(session, team_id: int | None) -> None:
    if team_id is not None and session.get(Team, team_id) is None:
        raise HTTPException(status_code=400, detail=f"Team {team_id} does not exist")


@router.get("", response_model=list[HeroPublic], summary="List heroes")
def list_heroes(session: SessionDep, team_id: int | None = None,
                offset: int = Query(default=0, ge=0),
                limit: int = Query(default=10, ge=1, le=100)):
    """Return a paginated list, optionally filtered by team."""
    query = select(Hero).order_by(Hero.id)
    if team_id is not None:
        query = query.where(Hero.team_id == team_id)
    return session.exec(query.offset(offset).limit(limit)).all()


@router.get("/{hero_id}", response_model=HeroPublic, summary="Get one hero", responses=NOT_FOUND)
def read_hero(hero_id: int, session: SessionDep):
    """Return a hero by its **id**."""
    return get_hero_or_404(session, hero_id)


@router.post("", response_model=HeroPublic, status_code=status.HTTP_201_CREATED,
             summary="Create a hero", responses={400: {"description": "Team does not exist"}})
def create_hero(hero_in: HeroCreate, session: SessionDep):
    """Create a hero, validating its optional team reference."""
    check_team_exists(session, hero_in.team_id)
    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.patch("/{hero_id}", response_model=HeroPublic, summary="Partially update a hero",
              responses={**NOT_FOUND, 400: {"description": "Team does not exist"}})
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    """Change only supplied fields; team_id=null removes team membership."""
    hero = get_hero_or_404(session, hero_id)
    changes = hero_in.model_dump(exclude_unset=True)
    check_team_exists(session, changes.get("team_id"))
    hero.sqlmodel_update(changes)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a hero", responses=NOT_FOUND)
def delete_hero(hero_id: int, session: SessionDep):
    """Delete the selected hero, returning no response body."""
    hero = get_hero_or_404(session, hero_id)
    session.delete(hero)
    session.commit()
