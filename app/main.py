from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
