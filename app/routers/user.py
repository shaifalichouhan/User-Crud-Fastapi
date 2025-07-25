from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserLogin, Token
from app.utils.jwt import create_access_token, verify_token
from app.auth.deps import allow_admin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


@router.post("/", response_model=UserOut, dependencies=[Depends(allow_admin)])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hash(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserOut], dependencies=[Depends(allow_admin)])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.delete("/{user_id}", dependencies=[Depends(allow_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(allow_admin)])
def update_user(user_id: int, updated_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.first_name = updated_data.first_name
    user.last_name = updated_data.last_name
    user.email = updated_data.email
    user.password = bcrypt.hash(updated_data.password)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")
    if not bcrypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token = create_access_token({
        "sub": db_user.email,
        "user_id": db_user.id,
        "user_type": db_user.user_type
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": db_user.user_type
    }


@router.get("/check-role", response_model=dict, dependencies=[Depends(allow_admin)])
def check_user_role(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": user.email, "user_type": user.user_type}
