import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.auth.jwt_handler import get_current_user
from app.models.audit_log import log_request

logger = logging.getLogger("request_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        lang = getattr(request.state, "lang", "en")

        user_info = None
        auth_header = request.headers.get("Authorization")
        if auth_header and "Bearer" in auth_header:
            try:
                user_info = await get_current_user(token=auth_header.split(" ")[1])
            except Exception:
                user_info = {"user_id": "anonymous"}

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "user_id": user_info.get("id", "anonymous") if user_info else "anonymous",
            "lang": lang,
            "status_code": response.status_code,
            "execution_time_ms": round(process_time, 2)
        }

        # ✅ سجل في Console
        logger.info(f"{log_data}")

        # ✅ سجل في MongoDB
        await log_request(log_data)

        return response
