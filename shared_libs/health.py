from pymongo import MongoClient
import requests
import os

def check_mongo():
    """فحص اتصال MongoDB"""
    mongo_uri = os.getenv("MONGO_URI")
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return {"mongo": "connected"}
    except Exception as e:
        return {"mongo": f"unhealthy - {str(e)}"}

def check_n8n():
    """فحص اتصال n8n (يستخدم في workflows-service)"""
    n8n_url = os.getenv("N8N_URL", "http://n8n:5678")
    try:
        r = requests.get(n8n_url)
        if r.status_code == 200:
            return {"n8n": "connected"}
        else:
            return {"n8n": f"unhealthy - status {r.status_code}"}
    except Exception as e:
        return {"n8n": f"unhealthy - {str(e)}"}
