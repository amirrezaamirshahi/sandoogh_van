from fastapi import APIRouter
from app.models.models import UserResponse
from app.database.database import get_user_collection

router = APIRouter(prefix="/user-management", tags=["user-management"])

@router.get("/", response_model=list[UserResponse])
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
