from environs import Env
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from datetime import timedelta


env = Env()
env.read_env()

SECRET_KEY = env("SECRET_KEY")
ACCESS_TOKEN_EXPIRE = timedelta(minutes=5)
REFRESH_TOKEN_EXPIRE = timedelta(days=2)
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
