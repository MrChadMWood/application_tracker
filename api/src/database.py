# ./core/database.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import HTTPException, status
from src.settings import dbconn_config


class UnreachableDatabase(Exception):
    def __init__(self, message="The database is currently unreachable. Please try again later."):
        self.message = message
        super().__init__(self.message)

# Database session
SQLALCHEMY_DATABASE_URL = 'postgresql://{username}:{password}@{hostname}:{port}/{database}'.format(**dbconn_config)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database async session
SQLALCHEMY_DATABASE_ASYNC_URL = 'postgresql+asyncpg://{username}:{password}@{hostname}:{port}/{database}'.format(**dbconn_config)
async_engine = create_async_engine(SQLALCHEMY_DATABASE_ASYNC_URL)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
