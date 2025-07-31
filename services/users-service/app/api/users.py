from fastapi import APIRouter, status, Depends, Request
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserRole
from app.controllers.user_controller import signup_user, login_user
from app.auth.jwt_handler import get_current_user, require_role
from app.core.messages import get_message
from app.core.messages.codes import PROFILE_FETCHED, USER_ROLE_UPDATED, ROLES_LIST_FETCHED
from app.models.user import update_user_role

router = APIRouter(prefix="/users", tags=["Users"])

# ================================
# تسجيل مستخدم جديد (Signup)
# ================================
@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a new user after validating email and password."
)
async def signup(user_data: UserCreate, request: Request):
    result = await signup_user(user_data)
    return {**get_message(PROFILE_FETCHED, request), "data": result}

# ================================
# تسجيل الدخول (Login)
# ================================
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Logs in a user and returns a JWT access token."
)
async def login(user_data: UserLogin, request: Request):
    result = await login_user(user_data)
    return {**get_message(PROFILE_FETCHED, request), "data": result}

# ================================
# الملف الشخصي (Profile) - محمي
# ================================
@router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Returns the profile details of the currently logged in user."
)
async def profile(current_user: dict = Depends(get_current_user), request: Request = None):
    return {**get_message(PROFILE_FETCHED, request), "data": current_user}

# ================================
# منطقة الأدمن فقط
# ================================
@router.get("/admin-area", status_code=status.HTTP_200_OK)
async def admin_area(
    current_user: dict = Depends(lambda: require_role(["admin"])),
    request: Request = None
):
    return {**get_message("WELCOME_ADMIN", request), "user": current_user}

# ================================
# تعديل دور المستخدم - Admin Only
# ================================
@router.put("/role/{user_id}")
async def change_user_role(
    user_id: str,
    new_role: UserRole,
    request: Request,
    current_admin: dict = Depends(lambda: require_role(["admin"]))
):
    updated_user = await update_user_role(user_id, new_role)
    return {**get_message(USER_ROLE_UPDATED, request), "user": updated_user}

# ================================
# عرض قائمة الأدوار - Admin Only
# ================================
@router.get("/roles")
async def get_roles(
    request: Request,
    current_admin: dict = Depends(lambda: require_role(["admin"]))
):
    roles = [role.value for role in UserRole]
    return {**get_message(ROLES_LIST_FETCHED, request), "roles": roles, "count": len(roles)}
