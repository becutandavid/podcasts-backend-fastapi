from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ..models.users import User, UserTable


class UserRepository:
    def __init__(self, db_session: Engine) -> None:
        self.db_session = db_session

    def add_user(self, obj: User) -> UserTable:
        """add user to database

        Args:
            obj (User): user to add

        Raises:
            ValueError: username already exists
            ValueError: email already exists

        Returns:
            UserTable: added user
        """
        with Session(self.db_session) as session:
            user = UserTable.from_orm(obj)
            if self.get_user(user.username):
                raise ValueError("username already exists")
            elif self.get_user_by_email(user.email):
                raise ValueError("email already exists")
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user(self, username: str) -> UserTable | None:
        """get user by username

        Args:
            username (str): username

        Returns:
            UserTable | None: returns user or None if user not found
        """
        with Session(self.db_session) as session:
            user = session.exec(
                select(UserTable).where(UserTable.username == username)
            ).one_or_none()
            return user

    def get_user_by_email(self, email: str) -> UserTable | None:
        """get user by email

        Args:
            email (str): email

        Returns:
            UserTable | None: retursn user or None if user not found
        """
        with Session(self.db_session) as session:
            user = session.exec(
                select(UserTable).where(UserTable.email == email)
            ).one_or_none()
            return user

    def remove_user(self, user_id: int) -> bool:
        """remove user with user_id from db

        Args:
            user_id (int): id of user

        Returns:
            bool: True if user deleted, False if not.
        """
        with Session(self.db_session) as session:
            user = session.exec(select(UserTable).where(UserTable.id == user_id)).one()
            if user:
                session.delete(user)
                session.commit()
                return True
            return False
