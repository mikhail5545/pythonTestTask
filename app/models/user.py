import bcrypt
import os

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

import os


class Base(DeclarativeBase):
    pass


class User(Base):
    r"""This class represents sqlalchemy.orm model for database interactions.
        .. Fields:: 
            -`id: Mapped[int]`
            -`first_name: Mapped[str]`
            -`last_name: Mapped[str]`
            -`email: Mapped[str]`
            -`salt: Mapped[str]`
            -`password: Mapped[str]`
            -`created_at: Mapped[DateTime]`
            -`updated_at: Mapped[DateTime]`
        :param `salt`: is used to protect user password, generated in `set_password` function.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(128), unique=True)
    salt: Mapped[str] = mapped_column(String(128), nullable=True)
    password: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, first name='{self.first_name}', last name='{self.last_name}', email='{self.email}')>"


    def set_password(self, plain_password) -> None:
        r"""Generates unique `salt` for user instance and hashes `plain_password` with it.
            .. Returns:: 
                None  
            :param `plain_password`: str, user password
        """
        self.salt = bcrypt.gensalt().decode("utf-8")
        self.password = (bcrypt.hashpw(plain_password.encode('utf-8'), self.salt.encode('utf-8'))).decode("utf-8")

    
    def check_password(self, plain_password) -> bool:
        r"""Compares `plain_password` to `self.password`.
            .. Returns:: 
                bool
            :param `plain_password`: str, user password
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))
    