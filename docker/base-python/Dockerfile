# docker/base-python/Dockerfile
FROM python:3.12-slim AS base

# إعداد البيئة لتقليل مشاكل الإخراج والكاش
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /base

# نسخ ملف المكتبات المشتركة
COPY requirements-common.txt .

# تحديث pip وتثبيت المكتبات المشتركة
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-common.txt
