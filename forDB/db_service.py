from forDB.db_config import engine, Base, AsyncSessionLocal
from forDB.models import UserStatistics

from sqlalchemy import select



class DB:
    @staticmethod
    async def create_tables() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            return None

    @staticmethod
    async def insert_user(tg_id: int) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserStatistics).filter_by(tg_id=tg_id)
            )
            user = result.scalar_one_or_none()
            if user is None:
                user = UserStatistics(tg_id=tg_id)
                session.add(user)
                await session.commit()
            return None

    @staticmethod
    async def select_data(
            column_name: str = None,
            value: int = None,
            limit: int = None,
            offset: int = None,
            sort_by: str = "id",
            one: bool = False
    ) -> list | UserStatistics:
        async with AsyncSessionLocal() as session:
            if column_name:
                target = getattr(UserStatistics, column_name)
            else:
                target = UserStatistics

            stmt = select(target)

            if value is not None:
                filter_col = target if column_name else UserStatistics.tg_id
                stmt = stmt.where(filter_col.is_(value))

            # Сортировка
            sort_column = getattr(UserStatistics, sort_by)
            stmt = stmt.order_by(sort_column.desc())

            # Пагинация - хз че это (разбивка по страницам)
            stmt = stmt.limit(limit).offset(offset) # лимит сколько выдаст | оффсет с какой начать

            result = await session.execute(stmt) # Отправка в бд сука
            data = result.scalars().all()
            return data[0] if one and data else data

    @staticmethod
    async def update_data(tg_id: int, add_correct_answer: int=0, add_incorrect_answer: int=0) -> None:
        async with AsyncSessionLocal() as session:
            stmt = select(UserStatistics).filter_by(tg_id=tg_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user:
                user.correct_answers += add_correct_answer
                user.incorrect_answers += add_incorrect_answer

                await session.commit()
            return None