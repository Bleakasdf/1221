from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.handlers.common import db_session, ensure_allowed, user_from_message
from app.keyboards import main_menu
from app.services.stats_service import stats_text


router = Router()


@router.message(Command("stats"))
@router.message(lambda message: message.text == "📊 Статистика")
async def stats(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    with db_session() as session:
        user = user_from_message(session, message)
        text = stats_text(session, user)
    await message.answer(text, reply_markup=main_menu())
