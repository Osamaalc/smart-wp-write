from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import os
import logging

app = FastAPI(title="Smart WP API Gateway")

# =============================
# إعداد الـ Logging
# =============================
logger = logging.getLogger("api_gateway")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
logger.addHandler(handler)

# =============================
# إعدادات البيئة
# =============================
SERVICE_URLS = {
    "users": os.getenv("USERS_SERVICE_URL", "http://users-service:8000"),
    "projects": os.getenv("PROJECTS_SERVICE_URL", "http://projects-service:8000"),
    "workflows": os.getenv("WORKFLOWS_SERVICE_URL", "http://workflows-service:8000"),
    "billing": os.getenv("BILLING_SERVICE_URL", "http://billing-service:8000"),
    "notifications": os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8000")
}

# =============================
# Health Check
# =============================
@app.get("/health")
async def health():
    return {"status": "healthy", "gateway": "running"}

# =============================
# دالة البروكسي الموحدة
# =============================
async def proxy_request(request: Request, service_name: str, path: str):
    base_url = SERVICE_URLS[service_name]
    url = f"{base_url}/{path}"
    method = request.method
    headers = dict(request.headers)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if method in ["POST", "PUT", "PATCH"]:
                content = await request.body()
                resp = await client.request(method, url, headers=headers, content=content)
            else:
                resp = await client.request(method, url, headers=headers)

        logger.info(f"{method} {service_name}/{path} -> {resp.status_code}")

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )

    except httpx.RequestError as e:
        logger.error(f"Service {service_name} not reachable: {e}")
        raise HTTPException(status_code=502, detail=f"{service_name} service unavailable")

    except Exception as e:
        logger.error(f"Unexpected error proxying {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal Gateway Error")

# =============================
# المسارات الموحدة لكل خدمة
# =============================
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):
    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")
    return await proxy_request(request, service, path)
