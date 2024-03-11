from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    username: str
    password: str


class CreatedUser(BaseModel):
    name: str
    username: str


class AuthData(BaseModel):
    username: str
    password: str
