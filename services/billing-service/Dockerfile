FROM smart-wp-base:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# نسخ متطلبات الخدمة الخاصة فقط
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# نسخ كود الخدمة
COPY . .

# إضافة shared-libs للمسار
ENV PYTHONPATH="${PYTHONPATH}:/app/../shared-libs"

# تشغيل الخدمة
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
