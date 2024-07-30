from fastapi import FastAPI
from app.routers import auth_router, user_router, user_management_router, news_router

app = FastAPI()

#*User
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(user_management_router.router)

#*News
app.include_router(news_router.router)
