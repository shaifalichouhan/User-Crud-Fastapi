from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from app.schemas.user import UserType 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_type = payload.get("user_type")
        if email is None or user_type is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def is_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users are allowed to perform this action"
        )
    return current_user

async def allow_admin(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserType.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user
