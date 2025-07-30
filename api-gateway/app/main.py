from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI(title="Smart WP API Gateway")

# =============================
# إعدادات البيئة
# =============================
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8000")
PROJECTS_SERVICE_URL = os.getenv("PROJECTS_SERVICE_URL", "http://projects-service:8000")
WORKFLOWS_SERVICE_URL = os.getenv("WORKFLOWS_SERVICE_URL", "http://workflows-service:8000")
BILLING_SERVICE_URL = os.getenv("BILLING_SERVICE_URL", "http://billing-service:8000")
NOTIFICATIONS_SERVICE_URL = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8000")

# =============================
# Health Check
# =============================
@app.get("/health")
async def health():
    return {"status": "healthy", "gateway": "running"}

# =============================
# Proxy Routes
# =============================

async def proxy_request(request: Request, base_url: str, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{base_url}{path}"
        headers = dict(request.headers)
        method = request.method

        if method in ["POST", "PUT", "PATCH"]:
            data = await request.body()
            response = await client.request(method, url, headers=headers, content=data)
        else:
            response = await client.request(method, url, headers=headers)

        return response

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(path: str, request: Request):
    return await proxy_request(request, USERS_SERVICE_URL, f"/{path}")

@app.api_route("/projects/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def projects_proxy(path: str, request: Request):
    return await proxy_request(request, PROJECTS_SERVICE_URL, f"/{path}")

@app.api_route("/workflows/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def workflows_proxy(path: str, request: Request):
    return await proxy_request(request, WORKFLOWS_SERVICE_URL, f"/{path}")

@app.api_route("/billing/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def billing_proxy(path: str, request: Request):
    return await proxy_request(request, BILLING_SERVICE_URL, f"/{path}")

@app.api_route("/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def notifications_proxy(path: str, request: Request):
    return await proxy_request(request, NOTIFICATIONS_SERVICE_URL, f"/{path}")
