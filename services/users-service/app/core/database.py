from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    """
    إنشاء اتصال بـ MongoDB
    """
    db.client = AsyncIOMotorClient(settings.MONGO_URI)
    db.db = db.client[settings.MONGO_DB_NAME]
    print(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")

async def close_mongo_connection():
    """
    إغلاق اتصال MongoDB
    """
    if db.client:
        db.client.close()
        print("❌ MongoDB connection closed")
