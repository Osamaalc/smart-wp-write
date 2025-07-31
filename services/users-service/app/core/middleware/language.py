from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.messages import DEFAULT_LANG, MESSAGES


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # قراءة Accept-Language من الهيدر
        lang_header = request.headers.get("Accept-Language", DEFAULT_LANG)
        lang = lang_header.split(",")[0].strip().lower()

        # إذا اللغة غير موجودة في MESSAGES نستخدم الافتراضية
        request.state.lang = lang if lang in MESSAGES else DEFAULT_LANG

        response = await call_next(request)
        return response
