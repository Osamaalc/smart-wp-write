from . import codes as C

MESSAGES_AR = {
    # Success
    C.USER_CREATED: {"code": C.USER_CREATED, "message": "تم إنشاء المستخدم بنجاح"},
    C.USER_LOGGED_IN: {"code": C.USER_LOGGED_IN, "message": "تم تسجيل الدخول بنجاح"},
    C.PROFILE_FETCHED: {"code": C.PROFILE_FETCHED, "message": "تم جلب الملف الشخصي بنجاح"},

    # Errors
    C.EMAIL_EXISTS: {"code": C.EMAIL_EXISTS, "message": "البريد الإلكتروني مسجل مسبقًا"},
    C.INVALID_CREDENTIALS: {"code": C.INVALID_CREDENTIALS, "message": "البريد الإلكتروني أو كلمة المرور غير صحيحة"},
    C.USER_NOT_FOUND: {"code": C.USER_NOT_FOUND, "message": "المستخدم غير موجود"},
    C.INVALID_ROLE: {"code": C.INVALID_ROLE, "message": "الدور المحدد غير صالح."},  # ✅ التعديل

    # General
    C.SERVER_ERROR: {"code": C.SERVER_ERROR, "message": "حدث خطأ غير متوقع"},
    C.UNAUTHORIZED: {"code": C.UNAUTHORIZED, "message": "غير مصرح لك بتنفيذ هذا الإجراء"},
    C.FORBIDDEN: {"code": C.FORBIDDEN, "message": "تم رفض الوصول"},

    C.USER_ROLE_UPDATED: {"code": C.USER_ROLE_UPDATED, "message": "تم تحديث دور المستخدم بنجاح"},
    C.ROLES_LIST_FETCHED: {"code": C.ROLES_LIST_FETCHED, "message": "تم جلب قائمة الأدوار بنجاح"},
    C.AUDIT_LOGS_FETCHED: {"code": C.AUDIT_LOGS_FETCHED, "message": "تم جلب سجلات التدقيق بنجاح"},



}
