from fastapi import Request
from .en import MESSAGES_EN
from .ar import MESSAGES_AR

DEFAULT_LANG = "en"

MESSAGES = {
    "en": MESSAGES_EN,
    "ar": MESSAGES_AR
}

def get_message(code: str, request: Request = None):
    """
    إرجاع الرسالة بناءً على الكود ولغة المستخدم
    """
    lang = getattr(request.state, "lang", DEFAULT_LANG) if request else DEFAULT_LANG
    return MESSAGES.get(lang, MESSAGES_EN).get(code, {"code": code, "message": "Unknown message"})
