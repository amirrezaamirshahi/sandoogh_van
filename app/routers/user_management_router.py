# routers/user_management_router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from app.models.models import UserResponse
from app.database.database import get_user_collection
from app.routers.user_router import get_current_user
from typing import Optional

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
