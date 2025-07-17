from pydantic import BaseModel

class UserCreat(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class userout(BaseModel):
    first_name: str
    last_name: str
    email: str

    class Config:
        orm_mode = True