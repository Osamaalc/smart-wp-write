from fastapi import HTTPException, status
from app.models.user import get_user_by_email, create_user, verify_password
from app.schemas.user import UserCreate, UserLogin
from app.auth.jwt_handler import create_access_token
from app.core.messages import get_message
from app.core.messages.codes import USER_CREATED, USER_LOGGED_IN, INVALID_CREDENTIALS, SERVER_ERROR, EMAIL_EXISTS
import logging

logger = logging.getLogger(__name__)

# ================================
# تسجيل مستخدم جديد
# ================================
async def signup_user(user_data: UserCreate):
    try:
        # تحقق من أن البريد غير مستخدم مسبقًا
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_message(EMAIL_EXISTS)
            )

        # إنشاء مستخدم جديد
        new_user = await create_user(user_data)
        return {
            **get_message(USER_CREATED),
            "data": new_user
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_message(SERVER_ERROR)
        )

# ================================
# تسجيل الدخول
# ================================
async def login_user(login_data: UserLogin):
    try:
        user = await get_user_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=get_message(INVALID_CREDENTIALS)
            )

        token_data = {
            "user_id": str(user["_id"]),
            "role": user.get("role", "user")
        }
        access_token = create_access_token(token_data)

        return {
            **get_message(USER_LOGGED_IN),
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_message(SERVER_ERROR)
        )
