from pydantic import BaseModel


class LoginUser(BaseModel):
    username: str
    password: str


class RegisterUser(BaseModel):
    username: str
    password1: str
    password2: str
