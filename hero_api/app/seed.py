from sqlmodel import SQLModel, Session
from app.database import engine
from app.models import Hero, Team

SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    team = Team(name="Avengers", headquarters="New York")
    session.add(team)
    session.commit()
    session.refresh(team)
    session.add(Hero(name="Tony", secret_name="Iron Man", age=45, team_id=team.id))
    session.add(Hero(name="Thor", secret_name="God of Thunder", age=150, team_id=team.id))
    session.commit()
print("Created example team and heroes.")
