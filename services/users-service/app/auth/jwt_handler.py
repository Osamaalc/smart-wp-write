from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from app.core.config import settings
from app.core.messages import get_message
from app.core.messages.codes import UNAUTHORIZED, USER_NOT_FOUND, FORBIDDEN
from app.models.user import users_collection, user_helper

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# ================================
# إنشاء Access Token
# ================================
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================================
# جلب المستخدم من DB
# ================================
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail=get_message(UNAUTHORIZED))

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail=get_message(USER_NOT_FOUND))

        return user_helper(user)
    except JWTError:
        raise HTTPException(status_code=401, detail=get_message(UNAUTHORIZED))


# ================================
# التحقق من الدور (RBAC)
# ================================
async def require_role(allowed_roles: list, current_user: dict = Depends(get_current_user)):
    """
    التحقق من أن المستخدم يملك أحد الأدوار المسموحة
    """
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(status_code=403, detail=get_message(FORBIDDEN))
    return current_user
