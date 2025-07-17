from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from app import model
from app import database
from app import schemes

model.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


def get_db():
    db = database.sessionlocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=schemes.userout)
def create_user(user: schemes.UserCreat, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hash(user.password)
    db_user = model.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
