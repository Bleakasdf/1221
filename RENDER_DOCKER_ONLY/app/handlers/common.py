from aiogram.types import Message
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import User
from app.services.workout_service import get_or_create_user


async def ensure_allowed(message: Message) -> bool:
    allowed = get_settings().allowed_ids
    if allowed and message.from_user.id not in allowed:
        await message.answer("Доступ закрыт.")
        return False
    return True


def db_session() -> Session:
    return SessionLocal()


def user_from_message(session: Session, message: Message) -> User:
    return get_or_create_user(session, message.from_user)
