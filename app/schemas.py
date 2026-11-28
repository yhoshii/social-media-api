from datetime import datetime
from typing import Literal

from pydantic import (  # thanks to BaseModel we can check the input of a client
    BaseModel,
    ConfigDict,
    EmailStr,
)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponce(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )  # we need it here so it converts sqlalchemy model to dictionary


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponce

    model_config = ConfigDict(from_attributes=True)


class PostResponce(BaseModel):
    Post: Post
    votes: int

    model_config = ConfigDict(
        from_attributes=True
    )  # we need it here so it converts sqlalchemy model to dictionary


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None


class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]


class Comment(BaseModel):
    comment: str


class CommentResponse(Comment):
    id: int
    post_id: int
    owner_id: int
    owner: UserResponce
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
