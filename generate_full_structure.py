import os

# ============================
# تعريف الهيكلية للخدمات
# ============================

services = {
    "users-service": ["api", "controllers", "models", "schemas", "auth", "core", "tests"],
    "projects-service": ["api", "controllers", "models", "schemas", "services", "core", "tests"],
    "workflows-service": ["api", "controllers", "models", "schemas", "services", "core", "tests"],
    "billing-service": ["api", "controllers", "models", "schemas", "services", "core", "tests"],
    "notifications-service": ["api", "controllers", "schemas", "services", "core", "tests"]
}

api_gateway = ["routes", "core", "tests"]

shared_libs = ["auth", "logger", "helpers", "validators"]

# ============================
# قوالب الملفات الأساسية
# ============================

placeholder_python = "# Placeholder Python File\n"

dockerfile_template = """FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "-m", "app.api"]
"""

requirements_template = """fastapi
uvicorn
pydantic
"""

config_template = """import os

class Config:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Service")
    DB_URI = os.getenv("DB_URI", "mongodb://localhost:27017")
"""

database_template = """# Database connection placeholder
def init_db():
    print("Initializing DB connection...")
"""

main_template = """from fastapi import FastAPI

app = FastAPI(title="API Gateway")

@app.get("/health")
def health_check():
    return {"status": "ok"}
"""

# ============================
# دوال إنشاء الملفات والمجلدات
# ============================

def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)

def create_service_structure(service_name, folders):
    base_service = os.path.join("services", service_name, "app")
    for folder in folders:
        os.makedirs(os.path.join(base_service, folder), exist_ok=True)
        # إضافة ملف __init__.py لكل مجلد Python
        create_file(os.path.join(base_service, folder, "__init__.py"), "")
    # ملفات أساسية
    create_file(os.path.join("services", service_name, "Dockerfile"), dockerfile_template)
    create_file(os.path.join("services", service_name, "requirements.txt"), requirements_template)
    create_file(os.path.join(base_service, "core", "config.py"), config_template)
    create_file(os.path.join(base_service, "core", "database.py"), database_template)

def create_api_gateway():
    base_gateway = os.path.join("api-gateway", "app")
    for folder in api_gateway:
        os.makedirs(os.path.join(base_gateway, folder), exist_ok=True)
        create_file(os.path.join(base_gateway, folder, "__init__.py"), "")
    create_file(os.path.join("api-gateway", "Dockerfile"), dockerfile_template)
    create_file(os.path.join("api-gateway", "requirements.txt"), requirements_template)
    create_file(os.path.join(base_gateway, "main.py"), main_template)

def create_shared_libs():
    for lib in shared_libs:
        os.makedirs(os.path.join("shared_libs", lib), exist_ok=True)
        create_file(os.path.join("shared_libs", lib, "__init__.py"), "")

# ============================
# تنفيذ
# ============================

def main():
    print("📌 إنشاء API Gateway...")
    create_api_gateway()

    print("📌 إنشاء الخدمات...")
    for service, folders in services.items():
        create_service_structure(service, folders)

    print("📌 إنشاء مكتبات مشتركة...")
    create_shared_libs()

    create_file("docker-compose.yml", "# Docker Compose Placeholder\n")
    create_file("README.md", "# Smart WP Write Project\n")

    print("✅ تم إنشاء جميع المجلدات والملفات بنجاح!")

if __name__ == "__main__":
    main()
