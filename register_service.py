from fastapi import FastAPI, HTTPException, Form
import base64
from pydantic import BaseModel
import httpx

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PHOTO_SERVICE_URL = os.environ.get('PHOTO_SERVICE_URL')
VIDEO_SERVICE_URL = os.environ.get('VIDEO_SERVICE_URL')
PROFANITY_SERVICE_URL = os.environ.get('PROFANITY_SERVICE_URL')
MESSAGE_SERVICE_URL = os.environ.get('MESSAGE_SERVICE_URL')

photo = False
video = False
profanity = False
message = False
authentication = False
app = FastAPI()


class GetService(BaseModel):
    service_name: str


class RegisterService(BaseModel):
    service_name: str


@app.get("/health")
async def get_service(data: GetService):
    return True


@app.get("/get_service/{service_name}")
async def get_service(service_name: str):
    print(service_name)
    try:
        global photo, video, profanity, message, authentication
        if service_name == "photo_service" and photo:
            return {"address": str(os.environ.get('PHOTO_SERVICE_URL')), "is_active": True}
        if service_name == "video_service" and video:
            return {"address": str(os.environ.get('VIDEO_SERVICE_URL')), "is_active": True}
        if service_name == "profanity_service" and profanity:
            return {"address": str(os.environ.get('VIDEO_SERVICE_URL')), "is_active": True}
        if service_name == "auth_service" and authentication:
            return {"address": str(os.environ.get('AUTH_SERVICE_URL')), "is_active": True}
        if service_name == "message_service" and message:
            return {"address": str(os.environ.get('MESSAGE_SERVICE_URL')), "is_active": True}

        return False

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register_service/{service_name}")
async def register_service(service_name: str):
    try:
        global photo, video, profanity, message, authentication
        if service_name == "photo_service":
            photo = True
            print(photo)
            return {"is_active": "True"}
        if service_name == "video_service":
            video = True
            return {"is_active": "True"}
        if service_name == "profanity_service":
            profanity = True
            return {"is_active": "True"}
        if service_name == "auth_service":
            authentication = True
            return {"is_active": "True"}
        if service_name == "message_service":
            message = True
            return {"is_active": "True"}

        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting Service...")
    # uvicorn register_service:app --reload --host 127.0.0.1 --port 8050