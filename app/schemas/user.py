from pydantic import BaseModel, ConfigDict

# User Schemas
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int  
    first_name: str
    last_name: str
    email: str

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

