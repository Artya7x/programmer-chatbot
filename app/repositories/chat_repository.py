from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.chat_models import History
from sqlalchemy.future import select

async def save_conversation(db: AsyncSession, query: str, response: str, user_id: int, cfg_image_url: str = None, dfg_image_url: str = None, reasoning: str = None):
    new_history = History(user_id=user_id,message_text=query,response_text=response, cfg_image_url=cfg_image_url, dfg_image_url=dfg_image_url, reasoning = reasoning)
    db.add(new_history)
    try:
        await db.commit()
        await db.refresh(new_history)
        return new_history
    except IntegrityError:
        await db.rollback()
        return None

async def get_conversation_history(db: AsyncSession, user_id: int):
    """Fetches the conversation history for a user, ordered by timestamp."""
    result = await db.execute(
        select(History.message_text, History.response_text, History.cfg_image_url, History.dfg_image_url, History.reasoning)
        .where(History.user_id == user_id)
        .order_by(History.timestamp.asc())
    )
    history = result.all()
    return [(row[0], row[1], row[2], row[3], row[4]) for row in history]