from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    description: str
    image: str
    price: float

class ProductCreate(ProductBase):
    pass

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    image: str
    price: float

    class Config:
        orm_mode = True
