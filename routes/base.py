from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings
import os


# Create router for the base endpoints
base_router = APIRouter(
    prefix="/api/v1",  # Prefix for the route
    tags=["api_v1"]    # Tag for documentation
)


@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    """
    A welcome endpoint that returns the application name and version.

    :param app_settings: The application settings loaded from the environment.
    :return: A dictionary with the application name and version.
    """
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_version": app_version,
    }
