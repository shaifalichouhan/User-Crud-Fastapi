from sqlalchemy import Column, Integer, String
from app.database import Base
import enum
from sqlalchemy import Enum
    
class UserTypeEnum(str, enum.Enum):
    admin = "admin"
    normal = "normal"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    user_type = Column(Enum(UserTypeEnum), default="normal")