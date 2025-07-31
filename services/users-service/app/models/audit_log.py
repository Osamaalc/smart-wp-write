from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import db

audit_collection: AsyncIOMotorCollection = db.get_collection("audit_logs")

async def log_request(data: dict):
    data["timestamp"] = datetime.utcnow()
    await audit_collection.insert_one(data)

async def get_audit_logs(user_id: str = None, path: str = None, limit: int = 50):
    """
    جلب سجلات الطلبات مع الفلترة
    """
    query = {}
    if user_id:
        query["user_id"] = user_id
    if path:
        query["path"] = {"$regex": path}

    cursor = audit_collection.find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    return logs
