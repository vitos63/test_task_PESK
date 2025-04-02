from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.models import User
from services.authorization.settings import pwd_context


async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await db.execute(select(User).where(username=username))
    if user:
        return pwd_context.verify(password, user.password)

    return False
