import os

class Config:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Service")
    DB_URI = os.getenv("DB_URI", "mongodb://localhost:27017")
