from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# ================================
# Enum للأدوار
# ================================
class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    editor = "editor"  # مثال دور إضافي إذا احتجنا مستقبلاً

# ================================
# تسجيل مستخدم جديد (Signup)
# ================================
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

# ================================
# تسجيل دخول (Login)
# ================================
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ================================
# استجابة المستخدم (Response)
# ================================
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# ================================
# البيانات الداخلية (يحتوي كلمة المرور المشفرة)
# ================================
class UserInDB(UserResponse):
    hashed_password: str

# ================================
# تعديل دور المستخدم (Admin Only)
# ================================
class UserRoleUpdate(BaseModel):
    role: UserRole = Field(..., description="الدور الجديد للمستخدم (user, admin, editor)")
