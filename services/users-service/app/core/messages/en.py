from . import codes as C

MESSAGES_EN = {
    # Success
    C.USER_CREATED: {"code": C.USER_CREATED, "message": "User created successfully"},
    C.USER_LOGGED_IN: {"code": C.USER_LOGGED_IN, "message": "User logged in successfully"},
    C.PROFILE_FETCHED: {"code": C.PROFILE_FETCHED, "message": "User profile retrieved successfully"},

    # Errors
    C.EMAIL_EXISTS: {"code": C.EMAIL_EXISTS, "message": "Email already registered"},
    C.INVALID_CREDENTIALS: {"code": C.INVALID_CREDENTIALS, "message": "Invalid email or password"},
    C.USER_NOT_FOUND: {"code": C.USER_NOT_FOUND, "message": "User not found"},
    C.INVALID_ROLE: {"code": C.INVALID_ROLE, "message": "Invalid role specified"},

    # General
    C.SERVER_ERROR: {"code": C.SERVER_ERROR, "message": "An unexpected error occurred"},
    C.UNAUTHORIZED: {"code": C.UNAUTHORIZED, "message": "You are not authorized to perform this action"},
    C.FORBIDDEN: {"code": C.FORBIDDEN, "message": "Access denied"},
    C.USER_ROLE_UPDATED: {"code": C.USER_ROLE_UPDATED, "message": "User role updated successfully"},
    C.ROLES_LIST_FETCHED: {"code": C.ROLES_LIST_FETCHED, "message": "Roles list fetched successfully"},
    C.AUDIT_LOGS_FETCHED: {"code": C.AUDIT_LOGS_FETCHED, "message": "Audit logs fetched successfully"},


}
