from fastapi import FastAPI
from app.routers import auth_router, user_router, user_management_router

app = FastAPI()

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(user_management_router.router)
