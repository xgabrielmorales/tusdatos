from pydantic import BaseModel


class CreateUser(BaseModel):
    name: str
    document_num: str
    username: str
    password: str


class CreatedUser(BaseModel):
    name: str
    document_num: str
    username: str


class AuthData(BaseModel):
    username: str
    password: str
