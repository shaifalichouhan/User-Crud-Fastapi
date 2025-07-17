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

@app.get("/users", response_model=list[schemes.userout])
def get_users(db: Session = Depends(get_db)):
    users = db.query(model.User).all()
    return users

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

@app.put("/users/{user_id}", response_model=schemes.userout)
def update_user(user_id: int, updated_data: schemes.UserCreat, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.first_name = updated_data.first_name
    user.last_name = updated_data.last_name
    user.email = updated_data.email
    user.password = bcrypt.hash(updated_data.password)

    db.commit()
    db.refresh(user)
    return user
