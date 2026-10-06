from sqlmodel import Field, Relationship, SQLModel


# 1. LINK TABLE (Bảng trung gian Many-to-Many)
class HeroMissionLink(SQLModel, table=True):
    hero_id: int | None = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    mission_id: int | None = Field(
        default=None, foreign_key="mission.id", primary_key=True
    )


# 2. TEAM MODELS
class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True)
    headquarters: str


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamPublic(TeamBase):
    id: int


# 3. MISSION MODELS
class MissionBase(SQLModel):
    title: str


class Mission(MissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(
        back_populates="missions", link_model=HeroMissionLink
    )


class MissionCreate(MissionBase):
    pass


class MissionPublic(MissionBase):
    id: int


# 4. HERO MODELS
class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    power: str | None = None  # <--- THÊM DÒNG NÀY

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team: Team | None = Relationship(back_populates="heroes")
    missions: list[Mission] = Relationship(
        back_populates="heroes", link_model=HeroMissionLink
    )


class HeroCreate(HeroBase):
    pass


class HeroPublic(HeroBase):
    id: int


class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: int | None = None
    power: str | None = None  # <--- THÊM DÒNG NÀY