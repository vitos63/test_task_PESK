from fastapi import APIRouter, Response, Request, Depends

from database.database import get_redis
from models.models import Role
from services.authorization.permissions import PermissionCheker
from services.authorization.auth_required import auth_required


router = APIRouter()


@router.get("/some_resource/")
@auth_required
@PermissionCheker(Role.USER.name)
async def some_resource(request: Request, response: Response, redis=Depends(get_redis)):
    return {"message": "Welcome to this resource"}


@router.get("/some_admin_resource/")
@auth_required
@PermissionCheker(Role.ADMIN.name)
async def some_resource(request: Request, response: Response, redis=Depends(get_redis)):
    return {"message": "Welcome to admin resource"}
