from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError
from app.models.models import UserCreate, User
from app.database.database import get_user_collection
from app.auth.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES  # اضافه کردن ایمپورت ثابت
import uuid  # برای تولید کد عضویت یونیک

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
    user_data["created_at"] = datetime.utcnow()  # اضافه کردن زمان فعلی به عنوان تاریخ ایجاد
    user_data["membership_code"] = str(uuid.uuid4())  # تولید کد عضویت یونیک

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

    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if remember_me:
        token_expires = timedelta(days=30)

    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=token_expires)
    user_data = {
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],  # اضافه کردن تاریخ ایجاد به داده‌های کاربر
        "status": user["status"],  # اضافه کردن وضعیت کاربر
        "membership_code": user["membership_code"]  # اضافه کردن کد عضویت کاربر
    }
    return {"access_token": access_token, "token_type": "bearer", "user": user_data}