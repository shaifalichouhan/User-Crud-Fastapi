from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional


# User Schemas
class UserType(str, Enum):
    admin = "admin"
    normal = "normal"
    
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    user_type: Optional[UserType] = UserType.normal

class UserOut(BaseModel):
    id: int  
    first_name: str
    last_name: str
    email: str
    user_type: UserType

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: str
    image: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True

#Login Functionality
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int
    email: str
    user_type: str
