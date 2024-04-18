from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import httpx
import base64

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = os.environ.get('DATABASE_URI')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Pydantic model for message
class Message(BaseModel):
    sender_id: int
    recipient_id: int
    content: str


# SQLAlchemy model for message
class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer)
    recipient_id = Column(Integer)
    content = Column(Text)


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Create a new message
def create_message(db_session, message: Message):
    db_message = MessageDB(**message.dict())
    db_session.add(db_message)
    db_session.commit()
    db_session.refresh(db_message)
    return db_message


# Retrieve messages for a user
def get_messages_for_user(db_session, user_id: int):
    messages = db_session.query(MessageDB).filter(
        (MessageDB.sender_id == user_id) | (MessageDB.recipient_id == user_id)
    ).all()
    return messages


# API endpoint to send a message
@app.post("/send-message/")
async def send_message(message: Message):
    db = SessionLocal()
    try:
        db_message = create_message(db, message)
        return db_message
    finally:
        db.close()


# API endpoint to retrieve messages for a user
@app.get("/get-messages/{user_id}")
async def get_messages(user_id: int):
    db = SessionLocal()
    try:
        messages = get_messages_for_user(db, user_id)
        return messages
    finally:
        db.close()


# async def make_http_request():
#     async with httpx.AsyncClient() as client:
#         payload = {"service_name": "photo_service"}  # Add service_name field with a value
#         response = await client.post('http://127.0.0.1:8000/register', json=payload)
#
#         if response.status_code != 200:
#             raise HTTPException(status_code=500,
#                                 detail=f"Failed to make HTTP request, status code: {response.status_code}")
#
#         print("successfully registered")
#
#
# @app.on_event("startup")
# async def startup_event():
#     await make_http_request()


if __name__ == "__main__":
    print("Starting Service...")
    # uvicorn message_service:app --reload --host 127.0.0.1 --port 8052
