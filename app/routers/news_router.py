# app/routers/news_router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.models.models import News
from app.database.database import get_news_collection
from app.routers.user_router import get_current_user
from app.routers.user_management_router import admin_only

router = APIRouter(prefix="/modules-content/news", tags=["news"])

@router.post("/add-news", response_model=News, dependencies=[Depends(admin_only)])
def create_news(news: News, current_user: dict = Depends(get_current_user)):
    news_data = news.dict()
    news_data["created_by"] = current_user.username
    get_news_collection().insert_one(news_data)
    return News(**news_data)

@router.get("/members-panel/news", response_model=list[dict])
def get_news_titles():
    news_list = list(get_news_collection().find({}, {
        "title": 1,
        "created_by": 1,
        "publish_date": 1,
        "status": 1
    }))

    for news in news_list:
        news['_id'] = str(news['_id'])

    return news_list

@router.get("/search", response_model=list[News])
def search_news(
    title: Optional[str] = Query(None, description="عنوان خبر"),
    access_level: Optional[str] = Query(None, description="سطح دسترسی"),
    status: Optional[str] = Query(None, description="وضعیت خبر")
):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if access_level:
        query["access_level"] = access_level
    if status:
        query["status"] = status

    news_list = list(get_news_collection().find(query))

    for news in news_list:
        news['_id'] = str(news['_id'])

    return news_list

@router.get("/members-panel/news/search", response_model=list[dict])
def search_news_by_title(title: str = Query(..., description="عنوان خبر")):
    query = {"title": {"$regex": title, "$options": "i"}}
    
    news_list = list(get_news_collection().find(query, {
        "title": 1,
        "created_by": 1,
        "publish_date": 1,
        "status": 1
    }))

    for news in news_list:
        news['_id'] = str(news['_id'])

    return news_list
