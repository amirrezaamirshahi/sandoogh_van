# app/routers/news_router.py
from fastapi import APIRouter, HTTPException, Depends
from app.models.models import News
from app.database.database import get_news_collection
from app.routers.user_router import get_current_user

router = APIRouter(prefix="/modules-content/news", tags=["news"])

@router.post("/add-news", response_model=News)
def create_news(news: News, current_user: dict = Depends(get_current_user)):
    news_data = news.dict()
    news_data["created_by"] = current_user.username
    get_news_collection().insert_one(news_data)
    return News(**news_data)

@router.get("/{news_id}", response_model=News)
def read_news(news_id: str):
    news = get_news_collection().find_one({"_id": news_id})
    if news is None:
        raise HTTPException(status_code=404, detail="News not found")
    return News(**news)

@router.get("/members-panel/news", response_model=list[dict])
def get_news_titles():
    news_list = list(get_news_collection().find({}, {
        "title": 1,
        "created_by": 1,
        "publish_date": 1
    }))

    # تبدیل ObjectId به رشته
    for news in news_list:
        news['_id'] = str(news['_id'])

    return news_list