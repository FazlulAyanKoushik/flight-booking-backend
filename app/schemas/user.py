from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    moderator = "moderator"
    enduser = "enduser"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.enduser

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
