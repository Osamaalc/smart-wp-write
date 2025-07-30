from fastapi import FastAPI
from shared_libs.health import check_mongo, check_n8n

app = FastAPI()

@app.get("/health")
def health():
    status = {"service": "workflows-service", "status": "healthy"}
    mongo_status = check_mongo()
    n8n_status = check_n8n()

    if ("unhealthy" in mongo_status.get("mongo", "")) or ("unhealthy" in n8n_status.get("n8n", "")):
        status["status"] = "unhealthy"

    status.update(mongo_status)
    status.update(n8n_status)
    return status
