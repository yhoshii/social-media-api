from pydantic import BaseModel, EmailStr, ConfigDict #thanks to BaseModel we can check the input of a client
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponce(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  #we need it here so it converts sqlalchemy model to dictionary


class UserLogin(BaseModel):
    email: EmailStr
    password: str



class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True 


class PostCreate(PostBase):
    pass


class PostResponce(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponce

    model_config = ConfigDict(from_attributes=True)  #we need it here so it converts sqlalchemy model to dictionary


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
