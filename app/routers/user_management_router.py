# routers/user_management_router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.models import UserResponse,GroupCreate, Group
from app.database.database import get_user_collection,get_group_collection
from app.routers.user_router import get_current_user
from typing import Optional
from datetime import datetime
from app.models.models import UserCreate, User
from app.auth.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import uuid  # برای تولید کد عضویت یونیک
from pymongo.errors import DuplicateKeyError

router = APIRouter(prefix="/user-management", tags=["user-management"])

def admin_only(current_user: dict = Depends(get_current_user)):
    if current_user.user_type != 'ادمین':
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    return current_user

@router.get("/", response_model=list[UserResponse], dependencies=[Depends(admin_only)])
def get_all_users():
    users = list(get_user_collection().find({}, {
        "first_name": 1,
        "last_name": 1,
        "membership_code": 1,
        "username": 1,
        "user_type": 1,
        "created_at": 1,
        "status": 1
    }))

    for user in users:
        user['_id'] = str(user['_id'])

    return users

@router.get("/search", response_model=list[UserResponse], dependencies=[Depends(admin_only)])
def search_users(
    first_name: Optional[str] = Query(None, description="نام"),
    last_name: Optional[str] = Query(None, description="نام خانوادگی"),
    username: Optional[str] = Query(None, description="نام کاربری"),
    status: Optional[str] = Query(None, description="وضعیت"),
    user_type: Optional[str] = Query(None, description="نوع کاربر"),
    category: Optional[str] = Query(None, description="دسته")
):
    query = {}

    if first_name:
        query["first_name"] = {"$regex": first_name, "$options": "i"}
    if last_name:
        query["last_name"] = {"$regex": last_name, "$options": "i"}
    if username:
        query["username"] = {"$regex": username, "$options": "i"}
    if status:
        query["status"] = status
    if user_type:
        query["user_type"] = user_type
    if category:
        query["category"] = category

    users = list(get_user_collection().find(query, {
        "first_name": 1,
        "last_name": 1,
        "membership_code": 1,
        "username": 1,
        "user_type": 1,
        "created_at": 1,
        "status": 1
    }))

    for user in users:
        user['_id'] = str(user['_id'])

    return users

@router.post("/groups/add-group", response_model=Group, dependencies=[Depends(admin_only)])
def add_group(group: GroupCreate):
    group_data = group.dict()
    group_data["created_at"] = datetime.utcnow()

    existing_group = get_group_collection().find_one({"group_name": group.group_name})
    if existing_group:
        raise HTTPException(status_code=400, detail="Group name already exists")

    valid_usernames = [user["username"] for user in get_user_collection().find({"username": {"$in": group.members}}, {"username": 1})]
    if len(valid_usernames) != len(group.members):
        raise HTTPException(status_code=400, detail="One or more usernames are invalid")

    get_group_collection().insert_one(group_data)
    return Group(**group_data)


@router.get("/groups", response_model=list[Group], dependencies=[Depends(admin_only)])
def get_all_groups():
    groups = list(get_group_collection().find({}, {
        "group_name": 1,
        "group_type": 1,
        "description": 1,
        "created_at": 1,
        "members": 1
    }))

    for group in groups:
        group['_id'] = str(group['_id'])

    return groups

@router.post("/add-user", response_model=User)
def register(user: UserCreate):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data.pop("password")
    user_data.pop("confirm_password")
    user_data["hashed_password"] = hashed_password
    # اضافه کردن زمان فعلی به عنوان تاریخ ایجاد
    user_data["created_at"] = datetime.utcnow()
    user_data["membership_code"] = str(uuid.uuid4())  # تولید کد عضویت یونیک

    # Check for unique username
    if get_user_collection().find_one({"username": user.username}):
        raise HTTPException(
            status_code=400, detail="Username already registered")

    try:
        get_user_collection().insert_one(user_data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    return User(**user_data)