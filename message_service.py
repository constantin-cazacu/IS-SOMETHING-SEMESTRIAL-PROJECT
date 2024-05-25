from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, VARCHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import httpx
import uuid
from datetime import datetime
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = os.environ.get('MESSAGE_DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Pydantic model for message
class Message(BaseModel):
    user_id: str
    participant_id: str
    content: str
    conversation_id: Optional[str] = None


# Pydantic model for creating conversation
class ConversationCreate(BaseModel):
    user_id: str
    participant_id: str


# SQLAlchemy model for message
class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(VARCHAR(36), primary_key=True, index=True)
    user_id = Column(VARCHAR(36))
    participant_id = Column(VARCHAR(36))
    content = Column(Text)
    timestamp = Column(DateTime)
    conversation_id = Column(VARCHAR(36))


# SQLAlchemy model for conversation
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(VARCHAR(36), primary_key=True, index=True)
    user_id = Column(VARCHAR(36))
    participant_id = Column(VARCHAR(36))


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Create a new message
def create_message(db_session, message: Message):
    # Check if the conversation already exists between sender and recipient
    conversation = db_session.query(Conversation).filter(
        ((Conversation.user_id == message.user_id) & (Conversation.participant_id == message.participant_id)) |
        ((Conversation.user_id == message.participant_id) & (Conversation.participant_id == message.user_id))
    ).first()

    # If conversation exists, use its ID, otherwise create a new conversation
    if conversation:
        conversation_id = conversation.id
    else:
        conversation = create_conversation(db_session, message.user_id, message.participant_id)
        conversation_id = conversation.id

    # Create the message with the associated conversation ID
    db_message = MessageDB(
        id=str(uuid.uuid4()),
        user_id=message.user_id,
        participant_id=message.participant_id,
        content=message.content,
        timestamp=datetime.utcnow(),
        conversation_id=conversation_id
    )
    db_session.add(db_message)
    db_session.commit()
    db_session.refresh(db_message)
    return db_message


# Create a new conversation
def create_conversation(db_session, user_id: str, participant_id: str):
    # Check if a conversation already exists between the provided user_id and participant_id
    existing_conversation = db_session.query(Conversation).filter(
        ((Conversation.user_id == user_id) & (Conversation.participant_id == participant_id)) |
        ((Conversation.user_id == participant_id) & (Conversation.participant_id == user_id))
    ).first()
    if existing_conversation:
        raise HTTPException(status_code=409, detail="Conversation already exists")

    # Create a new conversation if no existing conversation found
    db_conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        participant_id=participant_id
    )
    db_session.add(db_conversation)
    db_session.commit()
    db_session.refresh(db_conversation)
    return db_conversation


# Retrieve messages for a conversation
def get_messages_for_conversation(db_session, conversation_id: str):
    messages = db_session.query(MessageDB).filter(
        MessageDB.conversation_id == conversation_id
    ).all()
    return messages


# Retrieve conversations for a user
def get_conversations_for_user(db_session, user_id: str):
    conversations = db_session.query(Conversation).filter(
        (Conversation.user_id == user_id) | (Conversation.participant_id == user_id)
    ).all()
    return conversations


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


# API endpoint to retrieve conversations for a user
@app.get("/conversations/{user_id}")
async def list_conversations(user_id: str):
    db = SessionLocal()
    try:
        conversations = get_conversations_for_user(db, user_id)
        return conversations
    finally:
        db.close()


# Create endpoint for creating conversations
@app.post("/create-conversation/")
async def create_conversation_endpoint(conversation: ConversationCreate):
    db = SessionLocal()
    try:
        db_conversation = create_conversation(db, conversation.user_id, conversation.participant_id)
        return db_conversation
    finally:
        db.close()


async def make_http_request():
    async with httpx.AsyncClient() as client:
        payload = {"service_name": "message_service"}  # Add service_name field with a value
        response = await client.post(os.environ.get('GATEWAY_URL'), json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=500,
                                detail=f"Failed to make HTTP request, status code: {response.status_code}")

        print("successfully registered")


@app.on_event("startup")
async def startup_event():
    await make_http_request()


if __name__ == "__main__":
    print("Starting Service...")
    # uvicorn message_service:app --reload --host 127.0.0.1 --port 8053

# {
#     response:
#     {
#         user name,
#         count
#         msgs:
#         [
#             timestp int,
#             sender name
#             content
#         ]
#     }
# }