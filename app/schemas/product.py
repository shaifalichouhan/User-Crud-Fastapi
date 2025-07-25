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
    
class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True
