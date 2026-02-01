from forDB.db_config import engine, Base, AsyncSessionLocal
from forDB.models import UserStatistics

from sqlalchemy import select

class DB:
    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_user(tg_id: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserStatistics).filter_by(tg_id=tg_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                user = UserStatistics(tg_id=tg_id)
                session.add(user)
                await session.commit()

    @staticmethod
    async def select_user(tg_id: int):
        async with AsyncSessionLocal() as session:
            stmt = select(UserStatistics).filter_by(tg_id=tg_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def update_data(tg_id: int, add_correct_answer: int=0, add_incorrect_answer: int=0):
        async with AsyncSessionLocal() as session:
            stmt = select(UserStatistics).filter_by(tg_id=tg_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                user.correct_answers += add_correct_answer
                user.incorrect_answers += add_incorrect_answer

                await session.commit()
