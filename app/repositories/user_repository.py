from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.user_models import User

async def create_user(db: AsyncSession, username: str, email: str, hashed_password: str, conv_id: str, user_role: str):
    """Inserts a new user into the database."""
    new_user = User(username=username, email=email, password=hashed_password, conversation_id=conv_id, role=user_role)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        return None  # Username or email already exists

async def save_applicant_decision(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    db.add(user)
    await db.commit()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_conversation_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(
            User.conversation_id
        )
        .where(
            User.id == user_id
        )
    )
    return result.scalars().first()