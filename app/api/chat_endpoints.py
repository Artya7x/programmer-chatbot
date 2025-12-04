from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.repositories.user_repository import get_conversation_by_user_id, save_applicant_decision
from app.services.chat_service import process_chat_query
from app.repositories.chat_repository import save_conversation,get_conversation_history
from pydantic import BaseModel
import uuid
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
    response = process_chat_query(request.query,conversation_id,user.role)
    if not response:
        raise HTTPException(status_code=400, detail="Failed to generate response.")

    if isinstance(response, str):
        raise HTTPException(status_code=500, detail=response)

    if user.role == "generate code":
        message_id = str(uuid.uuid4())
        subdir = f"u{user.id}/c{conversation_id}"

        cfg_paths = {}
        dfg_paths = {}

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

        if hasattr(response, "cfg_graphs") and response.cfg_graphs:
            for graph_item in response.cfg_graphs:
                func_name = graph_item.function_name
                dot_src = graph_item.dot_source
                path = render_graph(dot_src, subdir, f"{message_id}_{func_name}_cfg")
                cfg_paths[func_name] = path
                content.append({
                    "type": "image",
                    "subtype": "cfg",
                    "function": func_name,
                    "url": path
                })

        if hasattr(response, "dfg_graphs") and response.dfg_graphs:
            for graph_item in response.dfg_graphs:
                func_name = graph_item.function_name
                dot_src = graph_item.dot_source
                path = render_graph(dot_src, subdir, f"{message_id}_{func_name}_dfg")
                dfg_paths[func_name] = path
                content.append({
                    "type": "image",
                    "subtype": "dfg",
                    "function": func_name,
                    "url": path
                })

        await save_conversation(
            db=db,
            query=request.query,
            response=response.python_code,
            user_id=user.id,
            cfg_image_urls=cfg_paths,
            dfg_image_urls=dfg_paths,
            reasoning=response.reasoning
        )

        return {"role": "assistant", "content": content}


    elif user.role == "optimize code":
        content = []

        if hasattr(response, "reasoning") and response.reasoning:
            content.append({
                "type": "text",
                "subtype": "reasoning",
                "text": response.reasoning
            })

        if hasattr(response, "python_code") and response.python_code.strip():
            content.append({
                "type": "code",
                "language": "python",
                "text": response.python_code
            })

        await save_conversation(
            db=db,
            query=request.query,
            response=response.python_code,
            user_id=user.id,
            cfg_image_url=None,
            dfg_image_url=None,
            reasoning=response.reasoning
        )

        return {"role": "assistant", "content": content}

@router.get("/history")
async def conversation_history(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    history = await get_conversation_history(db, user.id)
    if not history:
        return {
            "history": [
                {
                    "message": None,
                    "response": "Welcome! I am a chatbot programmed to assist you with Python code."
                }
            ]
        }

    formatted_history = []
    for message_text, response_text, cfg_urls, dfg_urls, reasoning in history:
        entry = {
            "message": message_text,
            "response": response_text,
            "cfg_image_urls": cfg_urls or {},
            "dfg_image_urls": dfg_urls or {},
            "reasoning": reasoning or "",
        }
        formatted_history.append(entry)

    return {"history": formatted_history}


@router.post("/chat/upload")
async def chat_upload(
    file: UploadFile = File(...),
    query: str = Form(""),
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handles chatbot requests with a Python file and optional user text."""
    if user.role == "generate code":
        raise HTTPException(status_code=403, detail="File uploads are not allowed for this role.")

    file_content = (await file.read()).decode("utf-8")

    # Combine file content and optional text message
    combined_input = file_content
    if query and query.strip():
        combined_input = f"# User prompt:\n{query.strip()}\n\n# Uploaded file content:\n{file_content}"

    request = ChatRequest(query=combined_input)

    return await chat(request, user, db)


@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    """Return basic info about the current user (role, username, id)."""
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }