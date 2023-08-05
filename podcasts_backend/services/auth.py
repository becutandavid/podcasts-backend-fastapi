from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..models.auth import TokenData
from ..models.users import User, UserInput, UserTable
from ..repository.db.postgres import engine
from ..repository.users import UserRepository

SECRET_KEY = "ff8bd256474ad33fc290ac0134a6aa36a3396fba7b7241d115f71610351ccabe"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

repository = UserRepository(engine)


def create_user(obj: UserInput) -> bool:
    try:
        user = User(
            username=obj.username,
            email=obj.email,
            password_hash=get_password_hash(obj.password),
        )
        repository.add_user(user)
        return True
    except ValueError:
        raise HTTPException(status_code=400, detail="User already exists")


def authenticate_user(username: str, password: str) -> UserTable:
    user = repository.get_user(username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserTable:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = repository.get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
