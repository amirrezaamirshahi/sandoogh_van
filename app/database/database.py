# app/database/database.py
from pymongo import MongoClient
from app.config.config import settings

client = MongoClient(settings.mongo_uri)
db = client.user_database

def get_user_collection():
    user_collection = db.users
    user_collection.delete_many({"username": None})
    user_collection.create_index("username", unique=True)
    return user_collection

def get_news_collection():
    news_collection = db.news
    news_collection.create_index("title")
    news_collection.create_index("access_level")
    news_collection.create_index("status")
    return news_collection

def get_group_collection():
    group_collection = db.groups
    group_collection.create_index("group_name", unique=True)
    return group_collection
