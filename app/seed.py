from sqlmodel import Session, SQLModel, select

from app.database import engine
from app.models import Hero, Mission, Team


def seed_data():
    # 1. Tạo các bảng nếu chưa có
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # 2. Kiểm tra nếu đã có ít nhất 1 team thì dừng script
        existing_team = session.exec(select(Team)).first()
        if existing_team:
            print("Database already seeded.")
            return

        # 3. Tạo 2 Teams
        team_avengers = Team(
            name="Avengers", headquarters="Avengers Tower"
        )
        team_justice = Team(
            name="Justice League", headquarters="Watchtower"
        )

        # 4. Tạo 2 Missions
        mission_sokovia = Mission(title="Battle of Sokovia")
        mission_doomsday = Mission(title="Defeat Doomsday")

        # 5. Tạo 5 Heroes và gán relationship (team, missions) trực tiếp
        hero_spiderman = Hero(
            name="Spider-Man",
            secret_name="Peter Parker",
            age=18,
            team=team_avengers,
            missions=[mission_sokovia],
        )
        hero_ironman = Hero(
            name="Iron Man",
            secret_name="Tony Stark",
            age=48,
            team=team_avengers,
            missions=[mission_sokovia],
        )
        hero_thor = Hero(
            name="Thor",
            secret_name="Thor Odinson",
            age=1500,
            team=team_avengers,
            missions=[mission_sokovia],
        )
        hero_batman = Hero(
            name="Batman",
            secret_name="Bruce Wayne",
            age=35,
            team=team_justice,
            missions=[mission_doomsday],
        )
        hero_superman = Hero(
            name="Superman",
            secret_name="Clark Kent",
            age=35,
            team=team_justice,
            missions=[mission_doomsday],
        )

        # 6. Thêm vào session và commit
        session.add_all(
            [
                hero_spiderman,
                hero_ironman,
                hero_thor,
                hero_batman,
                hero_superman,
            ]
        )
        session.commit()
        print("Successfully seeded the database!")


if __name__ == "__main__":
    seed_data()