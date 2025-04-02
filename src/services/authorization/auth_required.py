from fastapi import Request, Response

from functools import wraps

from services.authorization.jwt_tokens import verify_access_token


def auth_required(func):
    @wraps(func)
    async def wrapper(request: Request, response: Response, redis, *args, **kwargs):
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        user_agent = request.headers.get("User-Agent")

        verify_access_token(
            redis=redis,
            refresh_token=refresh_token,
            response=response,
            user_agent=user_agent,
            access_token=access_token,
        )
        return await func(request, response, redis, *args, **kwargs)

    return wrapper
