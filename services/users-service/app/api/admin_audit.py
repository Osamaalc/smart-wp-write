from fastapi import APIRouter, Depends, Query, Request
from app.auth.jwt_handler import require_role
from app.models.audit_log import get_audit_logs
from app.core.messages import get_message
from app.core.messages.codes import AUDIT_LOGS_FETCHED

router = APIRouter(prefix="/admin/audit", tags=["Admin Audit"])

@router.get("/logs")
async def fetch_audit_logs(
    request: Request,
    user_id: str = Query(None, description="فلترة حسب معرف المستخدم"),
    path: str = Query(None, description="فلترة حسب المسار"),
    limit: int = Query(50, description="عدد السجلات"),
    current_admin: dict = Depends(lambda: require_role(["admin"]))
):
    logs = await get_audit_logs(user_id=user_id, path=path, limit=limit)
    return {
        **get_message(AUDIT_LOGS_FETCHED, request),
        "count": len(logs),
        "logs": logs
    }
