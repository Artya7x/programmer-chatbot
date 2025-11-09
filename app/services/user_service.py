from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from openai import OpenAI

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_openai_conversation():
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY)
    conversation = client.conversations.create()
    conversation_id = conversation.id
    return conversation_id