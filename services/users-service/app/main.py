from fastapi import FastAPI
from shared_libs.health import check_mongo
from app.api import users, admin_audit
from app.core.middleware.language import LanguageMiddleware
from app.core.middleware.logging import RequestLoggingMiddleware
from app.core.database import connect_to_mongo, close_mongo_connection

app = FastAPI()

# Middlewares
app.add_middleware(LanguageMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Events for DB Connection
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/health")
def health():
    status = {"service": "users-service", "status": "healthy"}
    mongo_status = check_mongo()
    if "unhealthy" in mongo_status.get("mongo", ""):
        status["status"] = "unhealthy"
    status.update(mongo_status)
    return status

# Routers
app.include_router(users.router)
app.include_router(admin_audit.router)
