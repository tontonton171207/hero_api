from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.database import SessionDep, engine
from app.models import (
    Hero,
    HeroCreate,
    HeroMissionLink,
    HeroPublic,
    HeroUpdate,
    Mission,
    MissionCreate,
    MissionPublic,
    Team,
    TeamCreate,
    TeamPublic,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


# ==============================
# MISSION ENDPOINTS
# ==============================


# 1. CREATE MISSION
@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


# 2. ASSIGN HERO TO MISSION
@app.post(
    "/heroes/{hero_id}/missions/{mission_id}",
    status_code=204,
)
def assign_hero_to_mission(
    hero_id: int, mission_id: int, session: SessionDep
):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)

    if not hero or not mission:
        raise HTTPException(
            status_code=404, detail="Hero or Mission not found"
        )

    # Kiểm tra xem đã gán chưa, nếu chưa gán thì thêm vào link table
    link = session.get(HeroMissionLink, (hero_id, mission_id))
    if not link:
        new_link = HeroMissionLink(hero_id=hero_id, mission_id=mission_id)
        session.add(new_link)
        session.commit()

    return None


# 3. GET MISSIONS OF A HERO
@app.get(
    "/heroes/{hero_id}/missions", response_model=list[MissionPublic]
)
def list_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions


# ==============================
# TEAM ENDPOINTS
# ==============================


@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
        session.refresh(team)
        return team
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="Team with this name already exists"
        )


@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    teams = session.exec(select(Team)).all()
    return teams


@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def list_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes


# ==============================
# HERO ENDPOINTS
# ==============================


@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None,
):
    statement = select(Hero)

    if min_age is not None:
        statement = statement.where(Hero.age >= min_age)
    if team_id is not None:
        statement = statement.where(Hero.team_id == team_id)
    if name is not None:
        statement = statement.where(Hero.name.ilike(f"%{name}%"))

    statement = statement.offset(offset).limit(limit)
    heroes = session.exec(statement).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero_in.model_dump(exclude_unset=True)

    if "team_id" in hero_data and hero_data["team_id"] is not None:
        team = session.get(Team, hero_data["team_id"])
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    hero.sqlmodel_update(hero_data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    session.delete(hero)
    session.commit()
    return None