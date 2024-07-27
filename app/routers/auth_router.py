from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from app.models.models import UserCreate, User
from app.database.database import get_user_collection
from app.auth.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User)
def register(user: UserCreate):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data.pop("password")
    user_data.pop("confirm_password")
    user_data["hashed_password"] = hashed_password

    # Check for unique username
    if get_user_collection().find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    try:
        get_user_collection().insert_one(user_data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    return User(**user_data)

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), remember_me: bool = Form(False)):
    user = get_user_collection().find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Determine the expiration time for the token
    access_token_expires = timedelta(days=7) if remember_me else timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
