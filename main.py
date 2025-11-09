from fastapi import FastAPI
from app.api.chat_endpoints import router as chatbot_router
from app.api.user_endpoints import router as user_router
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="HR Chatbot App",
    description="An AI-powered chatbot for simulating a software engineering interview.",
    version="1.0.0"
)
app.include_router(chatbot_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/register")
def serve_register():
    return FileResponse("frontend/templates/register.html")

@app.get("/login")
def serve_login():
    return FileResponse("frontend/templates/login.html")

@app.get("/chat")
async def get_chat_page():
    return FileResponse("frontend/templates/chat.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)