from sqlalchemy.orm import Mapped, mapped_column

from forDB.db_config import Base



class UserStatistics(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True, index=True)
    correct_answers: Mapped[int] = mapped_column(default=0)
    incorrect_answers: Mapped[int] = mapped_column(default=0)