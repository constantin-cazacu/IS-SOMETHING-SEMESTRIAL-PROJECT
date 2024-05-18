from fastapi import FastAPI, HTTPException
import requests
import base64
from pydantic import BaseModel
import time
from typing import Optional

app = FastAPI()

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve URLs from environment variables
REGISTER_SERVICE_URL = os.environ.get('REGISTER_SERVICE_URL')


class ServiceRegister(BaseModel):
    service_name: str


class Message(BaseModel):
    user_id: str
    participant_id: str
    content: str
    conversation_id: Optional[str] = None


class VideoUpload(BaseModel):
    video: str
    description: str
    publish_date: int


class PhotoUpload(BaseModel):
    image: str
    description: str
    publish_date: int


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@app.post("/health")
async def urmom():
    return "sss"


@app.post("/register-user/")
async def register_user(user: UserCreate):
    response = requests.get(f"{REGISTER_SERVICE_URL}/get_service/auth_service")
    response_payload = response.json()
    print(response_payload)
    if response_payload["is_active"]:
        # print("service is registered")
        try:
            payload = {
                'username': user.username,
                'password': user.password,
            }

            response = requests.post(f'{response_payload["address"]}/register-user/', json=payload)

            if response.status_code == 200:
                return {"message": "User registered successfully"}
            elif response.status_code == 400:
                return {"message": "User already registered"}
            else:
                raise HTTPException(status_code=500, detail="Failed to register user")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/login/")
async def login_user(user: UserLogin):
    response = requests.get(f"{REGISTER_SERVICE_URL}/get_service/auth_service")
    response_payload = response.json()
    print(response_payload)
    if response_payload["is_active"]:
        # print("service is registered")
        try:
            payload = {
                'username': user.username,
                'password': user.password,
            }

            response = requests.post(f'{response_payload["address"]}/login/', json=payload)

            if response.status_code == 200:
                response_data = response.json()
                user_id = response_data.get('user_id')
                return {"message": "Login successful",
                        "user_id": user_id}
            else:
                raise HTTPException(status_code=500, detail="Login Failed")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/register")
async def register_service(data: ServiceRegister):
    print(data.service_name)
    payload = {
        'service_name': data.service_name
    }

    # headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{REGISTER_SERVICE_URL}/register_service/{data.service_name}")
    if response.status_code == 200:
        return {"message": "Service registered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to upload video")

    # return "urmom"


@app.post("/upload-video")
async def upload_video(data: VideoUpload):
    response = requests.get(f"{REGISTER_SERVICE_URL}/get_service/video_service")
    response_payload = response.json()
    print(response_payload)
    if response_payload["is_active"]:
        # print("service is registered")
        try:
            video_bytes = base64.b64decode(data.video.encode('utf-8'))

            payload = {
                'video': data.video,
                'description': data.description,
                'publish_date': data.publish_date,
                'uid': "data.uid"
            }

            response = requests.post(response_payload["address"], json=payload)

            if response.status_code == 200:
                return {"message": "Video uploaded successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to upload video")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/send-message/")
async def send_message(data: Message):
    response = requests.get(f"{REGISTER_SERVICE_URL}/get_service/message_service")
    response_payload = response.json()
    print(response_payload)
    if response_payload["is_active"]:
        # print("service is registered")
        try:
            payload = {
                'user_id': data.user_id,
                'participant_id': data.participant_id,
                'content': data.content,
                'conversation_id': data.conversation_id
            }

            response = requests.post(f'{response_payload["address"]}/send-message/', json=payload)

            if response.status_code == 200:
                return {"message": "Message sent successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to send message")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.get("/get-messages/{conversation_id}")
async def get_message(conversation_id: str):
    response = requests.get(f"{REGISTER_SERVICE_URL}/get_service/message_service")
    response_payload = response.json()
    print(response_payload)
    if response_payload["is_active"]:
        # print("service is registered")
        try:
            response = requests.get(f'{response_payload["address"]}/get-messages/{conversation_id}')

            if response.status_code == 200:
                return {"message": "Message received successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to get message")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="Service not found")


@app.post("/upload-photo/")
async def upload_photo(data: PhotoUpload):
    response = requests.get(f"{REGISTER_SERVICE_URL}/get_service/photo_service")
    response_payload = response.json()
    # print(response_payload)
    if response_payload["is_active"]:
        print("service is registered")
        try:
            image_bytes = base64.b64decode(data.image.encode('utf-8'))

            payload = {
                'image': data.image,
                'description': data.description,
                'publish_date': data.publish_date,
                'uid': "data.uid"

            }
            # print("sm")
            response = requests.post(response_payload["address"], json=payload)
            # print("sm")

            if response.status_code == 200:
                return {"message": "Photo uploaded successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to upload photo")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail="Service not found")


if __name__ == "__main__":
    print("Starting gateway...")
    # uvicorn gateway:app --reload --host 127.0.0.1 --port 8000
    # uvicorn.run(app, host="127.0.0.1", port=5000)