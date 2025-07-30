from sqlalchemy import Column, Integer, String, Float
from app.database import Base
import stripe


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    image = Column(String)
    price = Column(Float, nullable=False)
