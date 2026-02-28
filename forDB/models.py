from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from forDB.db_config import Base



class UserStatistics(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(default='not found')
    correct_answers: Mapped[int] = mapped_column(default=0)
    incorrect_answers: Mapped[int] = mapped_column(default=0)

    @hybrid_property
    def rank(self) -> int:
        return self.correct_answers * 15 - self.incorrect_answers * 10