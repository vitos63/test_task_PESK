from fastapi import HTTPException, status, Request, Response
import jwt

from functools import wraps
from typing import List

from models.models import Role
from services.authorization.settings import SECRET_KEY, ALGORITHM


class PermissionCheker:
    def __init__(self, roles: List[str]):
        self.roles = roles

    def __call__(self, func):
        @wraps(func)
        async def wrapper(request: Request, response: Response, redis, *args, **kwargs):

            refresh_token = request.cookies.get("refresh_token")
            decoded_refresh_token = jwt.decode(
                refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
            )
            user_role = decoded_refresh_token.get("role")
            if user_role == Role.ADMIN.name or user_role in self.roles:
                return await func(request, response, *args, **kwargs)

            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rules"
                )

        return wrapper
