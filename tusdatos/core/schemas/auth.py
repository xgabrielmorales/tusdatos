from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    username: str
    password: str


class CreatedUserData(BaseModel):
    name: str
    username: str


class AuthData(BaseModel):
    username: str
    password: str
