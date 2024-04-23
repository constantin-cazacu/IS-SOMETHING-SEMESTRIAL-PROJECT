from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import uuid
import hashlib

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# SQLAlchemy setup
DATABASE_URL = os.environ.get('AUTH_DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Pydantic model for user registration
class UserCreate(BaseModel):
    username: str
    password: str


# SQLAlchemy model for user
class User(Base):
    __tablename__ = "users"
    id = Column(VARCHAR(36), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(VARCHAR(128))


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Password hashing
def hash_password(password):
    # Hash the password using SHA-512
    hashed_password = hashlib.sha512(password.encode()).hexdigest()
    return hashed_password


# Function to verify passwords
def verify_password(plain_password, hashed_password):
    # Hash the plain password using SHA-512 and compare with the stored hashed password
    return hashed_password == hashlib.sha512(plain_password.encode()).hexdigest()


# Function to create a new user
def create_user(db_session, user: UserCreate):
    # Check if the username already exists
    existing_user = db_session.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    db_user = User(id=str(uuid.uuid4()),
                   username=user.username,
                   hashed_password=hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


# Function to get user data
def get_user(db_session, user_id: int):
    return db_session.query(User).filter(User.id == user_id).first()


# API endpoint for user registration
@app.post("/register/")
async def register(user: UserCreate):
    db = SessionLocal()
    try:
        db_user = create_user(db, user)
        return db_user
    finally:
        db.close()


# API endpoint to get user data
@app.get("/user/{user_id}")
async def get_user_data(user_id: str):
    db = SessionLocal()
    try:
        user = get_user(db, user_id)
        return user
    finally:
        db.close()

# async def make_http_request():
#     async with httpx.AsyncClient() as client:
#         payload = {"service_name": "auth_service"}  # Add service_name field with a value
#         response = await client.post('http://127.0.0.1:8000/register', json=payload)
#
#         if response.status_code != 200:
#             raise HTTPException(status_code=500,
#                                 detail=f"Failed to make HTTP request, status code: {response.status_code}")
#
#         print("successfully registered")



# @app.on_event("startup")
# async def startup_event():
#     # await make_http_request()
#     # Create tables in the database
#     # Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    print("Starting Service...")
    # uvicorn auth_service:app --reload --host 127.0.0.1 --port 8054
