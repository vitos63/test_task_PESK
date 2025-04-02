from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.database import get_db, get_redis
from models.models import User
from services.authorization.settings import pwd_context, REFRESH_TOKEN_EXPIRE
from schemas.users import RegisterUser, LoginUser
from services.authentication.authenticate import authenticate_user
from services.authorization.jwt_tokens import (
    create_access_token,
    create_refresh_token,
    set_tokens,
    delete_tokens,
)


router = APIRouter()


@router.post("/register/")
async def register(user: RegisterUser, db: AsyncSession = Depends(get_db)):
    if user.password1 != user.password2:
        return {"error": "Password1 and password2 must be equal"}

    new_user = User(username=user.username, password=pwd_context.hash(user.password1))
    db.add(new_user)
    await db.commit()
    return {"message": "User created"}


@router.post("/login/")
async def login(
    user: LoginUser,
    request:Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    if authenticate_user(user.username, user.password, db):
        result = await db.execute(select(User).where(User.username == user.username))
        user_role = result.first()[0].role.name
        user_agent = request.headers.get('User-Agent')
        access_token = create_access_token({"sub": user.username, "role": user_role, 'user_agent':user_agent})
        refresh_token = create_refresh_token({"sub": user.username, "role": user_role, 'user_agent':user_agent})
        set_tokens(access_token, refresh_token, response)
        redis.set(user.username, refresh_token, REFRESH_TOKEN_EXPIRE)
        
        return {"message": "Successfully logged in"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout/")
async def logout(response: Response):
    delete_tokens(response=response)
    return {"message": "Successfully logged out"}
