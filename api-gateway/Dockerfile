FROM python:3.10-slim

WORKDIR /app

# نسخ مكتبات مشتركة
COPY ../shared-libs/requirements-common.txt /shared-libs/requirements-common.txt

# نسخ ملف متطلبات الـ Gateway
COPY requirements.txt .

# تثبيت المكتبات المشتركة + الخاصة بالـ Gateway
RUN pip install --no-cache-dir -r /shared-libs/requirements-common.txt && \
    pip install --no-cache-dir -r requirements.txt

# نسخ كود الـ Gateway
COPY . /app

# إضافة shared-libs إلى المسار
ENV PYTHONPATH="${PYTHONPATH}:/app/../shared-libs"

# تشغيل API Gateway باستخدام Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
