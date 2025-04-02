from environs import Env
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import redis

env = Env()
env.read_env()

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 0


DATABASE_URL = env("DATABASE_URL")
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis():
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    try:
        yield redis_client

    finally:
        redis_client.close()
