from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings
import os


# إنشاء router للواجهات الأساسية
base_router = APIRouter(
    prefix="/api/v1",  # بادئة المسار
    tags=["api_v1"]   # وسم للتوثيق
)


@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    """
    واجهة ترحيبية تعرض اسم التطبيق وإصداره.
    """
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_version": app_version,
    }


