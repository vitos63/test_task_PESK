from fastapi import Depends, HTTPException, status, Response
import jwt

from datetime import datetime

from services.authorization.settings import (
    ACCESS_TOKEN_EXPIRE,
    REFRESH_TOKEN_EXPIRE,
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme,
)


def create_access_token(data: dict):
    data.update({"exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE, "type": "access"})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    data.update({"exp": datetime.now() + REFRESH_TOKEN_EXPIRE, "type": "refresh"})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(
    redis,
    refresh_token,
    response: Response,
    user_agent,
    access_token=Depends(oauth2_scheme),
):
    try:
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token["user_agent"] != user_agent:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return decoded_token

    except jwt.ExpiredSignatureError:
        verify_refresh_token(refresh_token, redis, response)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def verify_refresh_token(refresh_token, redis, response):
    try:
        decoded_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        redis_token = jwt.decode(
            redis.get(decoded_token["sub"]), SECRET_KEY, algorithms=[ALGORITHM]
        )
        if redis_token == decoded_token:
            new_refresh_token = create_refresh_token(
                {
                    "sub": decoded_token["sub"],
                    "role": decoded_token["role"],
                    "user_agent": decoded_token["user_agent"],
                }
            )
            new_access_token = create_access_token(
                {
                    "sub": decoded_token["sub"],
                    "role": decoded_token["role"],
                    "user_agent": decoded_token["user_agent"],
                }
            )
            redis.set(decoded_token["sub"], new_refresh_token, REFRESH_TOKEN_EXPIRE)
            set_tokens(new_access_token, new_refresh_token, response)

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token"
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def set_tokens(access_token, refresh_token, response: Response):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )


def delete_tokens(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
