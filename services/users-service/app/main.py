from fastapi import FastAPI
from shared_libs.health import check_mongo

app = FastAPI()

@app.get("/health")
def health():
    status = {"service": "users-service", "status": "healthy"}
    mongo_status = check_mongo()

    if "unhealthy" in mongo_status.get("mongo", ""):
        status["status"] = "unhealthy"

    status.update(mongo_status)
    return status
