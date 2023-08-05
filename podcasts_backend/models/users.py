from pydantic import BaseModel
from sqlmodel import VARCHAR, Column, Field, SQLModel


class UserInput(BaseModel):
    username: str
    email: str
    password: str


class User(BaseModel):
    username: str
    email: str
    password_hash: str


class UserOutput(BaseModel):
    username: str
    email: str


class UserTable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column("username", VARCHAR, unique=True, index=True)
    )
    email: str
    password_hash: str = ""
