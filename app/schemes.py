from pydantic import BaseModel, ConfigDict

class UserCreat(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class userout(BaseModel):
    id: int  
    first_name: str
    last_name: str
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

model_config = ConfigDict(from_attributes=True)