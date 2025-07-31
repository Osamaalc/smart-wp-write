from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException, status
from app.core.database import db
from app.schemas.user import UserCreate, UserRole
from passlib.context import CryptContext
from app.core.messages import get_message
from app.core.messages.codes import INVALID_ROLE

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_collection: AsyncIOMotorCollection = db.get_collection("users")

def user_helper(user) -> dict:
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role", UserRole.user),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at")
    }

async def create_user(user_data: UserCreate):
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise ValueError("Email already registered")

    hashed_password = pwd_context.hash(user_data.password)
    new_user = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "role": UserRole.user,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await users_collection.insert_one(new_user)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    return user_helper(created_user)

async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})

async def get_user_by_id(user_id: str):
    return await users_collection.find_one({"_id": ObjectId(user_id)})

async def update_user_role(user_id: str, new_role: UserRole):
    # ✅ تحقق من أن الدور المرسل موجود في Enum
    if new_role not in UserRole:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message(INVALID_ROLE)
        )

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role, "updated_at": datetime.utcnow()}}
    )
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return user_helper(updated_user)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
