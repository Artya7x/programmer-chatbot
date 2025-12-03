from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_models import History
from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.user_repository import get_conversation_by_user_id, save_applicant_decision
from app.services.chat_service import process_chat_query
from app.repositories.chat_repository import save_conversation,get_conversation_history
from pydantic import BaseModel
from datetime import datetime
import asyncio
import time
import csv
import os
import uuid
import json
from scripts.render_graphs import render_graph

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

    conversation_id = await get_conversation_by_user_id(db, user.id)
    response = process_chat_query(request.query,conversation_id)
    if not response:
        raise HTTPException(status_code=400, detail="Failed to generate response.")

    if user.role == "generate code":
        message_id = str(uuid.uuid4())
        subdir = f"u{user.id}/c{conversation_id}"

        cfg_path = None
        dfg_path = None

        # start content with reasoning if available
        content = []

        if hasattr(response, "reasoning") and response.reasoning:
            content.append({
                "type": "text",
                "subtype": "reasoning",
                "text": response.reasoning
            })

        if response.python_code and response.python_code.strip():
            content.append({
                "type": "code",
                "language": "python",
                "text": response.python_code
            })

        if response.cfg_graph and response.cfg_graph.strip():
            cfg_path = render_graph(response.cfg_graph, subdir, f"{message_id}_cfg")
            content.append({
                "type": "image",
                "subtype": "cfg",
                "url": cfg_path
            })

        if response.dfg_graph and response.dfg_graph.strip():
            dfg_path = render_graph(response.dfg_graph, subdir, f"{message_id}_dfg")
            content.append({
                "type": "image",
                "subtype": "dfg",
                "url": dfg_path
            })

        await save_conversation(
            db=db,
            query=request.query,
            response=response.python_code,
            user_id=user.id,
            cfg_image_url=cfg_path,
            dfg_image_url=dfg_path,
            reasoning=response.reasoning
        )

        return {"role": "assistant", "content": content}


    else:
        # TODO: implement other role logic here . :* <- this is an emoji ;)
        raise HTTPException(status_code=501, detail="Optimize code mode not implemented yet.")

@router.get("/history")
async def conversation_history(user = Depends(get_current_user) ,db: AsyncSession = Depends(get_db)):
    history = await get_conversation_history(db, user.id)
    if not history:
        return {"history": [{"message": None, "response": "Welcome! I am a chatbot programmed to assist you with python code" }]}

    formatted_history = []
    for h in history:
        message_text, response_text, cfg_url, dfg_url, reasoning = h
        entry = {
            "message": message_text,
            "response": response_text,
        }
        if cfg_url:
            entry["cfg_image_url"] = cfg_url
        if dfg_url:
            entry["dfg_image_url"] = dfg_url

        if reasoning:
            entry["reasoning"] = reasoning
        formatted_history.append(entry)

    return {"history": formatted_history}

