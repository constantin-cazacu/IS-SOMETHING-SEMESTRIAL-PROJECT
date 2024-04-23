from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, VARCHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import httpx
import base64
import uuid
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = os.environ.get('DATABASE_URL')
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
    id = Column(VARCHAR(36), primary_key=True, index=True)
    sender_id = Column(VARCHAR(36))
    recipient_id = Column(VARCHAR(36))
    content = Column(Text)
    timestamp = Column(DateTime)
    conversation_id = Column(VARCHAR(36))


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Create a new message
def create_message(db_session, message: Message):
    db_message = MessageDB(
        id=str(uuid.uuid4()),
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        content=message.content,
        timestamp=datetime.utcnow(),
        conversation_id=str(uuid.uuid4())
    )
    db_session.add(db_message)
    db_session.commit()
    db_session.refresh(db_message)
    return db_message


# Retrieve messages for a conversation
def get_messages_for_conversation(db_session, conversation_id: str):
    messages = db_session.query(MessageDB).filter(
        MessageDB.conversation_id == conversation_id
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


# API endpoint to retrieve messages for a conversation
@app.get("/get-messages/{conversation_id}")
async def get_messages(conversation_id: str):
    db = SessionLocal()
    try:
        messages = get_messages_for_conversation(db, conversation_id)
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
    # uvicorn message_service:app --reload --host 127.0.0.1 --port 8053
