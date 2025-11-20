from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.user_repository import get_conversation_by_user_id, save_applicant_decision
from app.services.chat_service import process_chat_query
from app.repositories.chat_repository import save_conversation,get_conversation_history
from pydantic import BaseModel
import asyncio

from scripts.send_email import send_email

router = APIRouter()

# Request model
class ChatRequest(BaseModel):
    query: str

# Chatbot endpoint
@router.post("/chat")
async def chat(request: ChatRequest,
               user = Depends(get_current_user) ,
               db: AsyncSession = Depends(get_db)):
    """Handles chatbot queries and returns AI-generated responses.
    """
    if user.decision in ("1", "0"):
        raise HTTPException(
            status_code=403,
            detail="This interview has already been concluded. You will receive an email with next steps."
        )
    conversation_id = await get_conversation_by_user_id(db, user.id)
    response = process_chat_query(request.query,conversation_id, user.role)
    if not response:
        raise HTTPException(status_code=400, detail="Failed to generate response.")

    if response.decision !="N/A":
        await save_applicant_decision(db,user.id,response.decision)
        send_email(user.email, response.decision, user.username)
    await save_conversation(db, request.query, response.response, user.id)

    return {
        "message": response.response,
        "decision": response.decision
    }


@router.get("/history")
async def conversation_history(user = Depends(get_current_user) ,db: AsyncSession = Depends(get_db)):
    history = await get_conversation_history(db, user.id)
    if not history:
        return {"history": [{"message": None, "response": "Welcome! I am a chatbot programmed to make an initial interview with you for the position you have selected. Are you ready to begin?" }]}
    return {"history" : [{"message" : h[0], "response" : h[1]} for h in history]}

@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return {"decision": user.decision}

