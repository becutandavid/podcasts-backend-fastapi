from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    password_hash: str


class UserInput(BaseModel):
    username: str
    email: str
    password: str


class UserOutput(BaseModel):
    username: str
    email: str


class UserOutputWithId(UserOutput):
    id: int
