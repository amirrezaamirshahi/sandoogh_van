# app/database/database.py
from pymongo import MongoClient
from app.config.config import settings

client = MongoClient(settings.mongo_uri)
db = client.user_database

def get_user_collection():
    """Get the user collection from the database."""
    user_collection = db.users
    # Remove documents with null username
    user_collection.delete_many({"username": None})
    user_collection.create_index("username", unique=True)
    return user_collection

def get_news_collection():
    """Get the news collection from the database."""
    news_collection = db.news
    return news_collection