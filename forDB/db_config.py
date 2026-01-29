from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from config import Config



class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    Config.DB_URL,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={
        "check_same_thread": False,
        "timeout": 3.0
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)