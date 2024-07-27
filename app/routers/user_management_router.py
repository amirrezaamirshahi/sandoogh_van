# routers/user_management_router.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.models import UserResponse
from app.database.database import get_user_collection
from app.routers.user_router import get_current_user  # برای دسترسی به کاربر فعلی

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

    # تبدیل ObjectId به رشته
    for user in users:
        user['_id'] = str(user['_id'])

    return users
