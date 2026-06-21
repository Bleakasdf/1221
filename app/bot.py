from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.handlers import export, nutrition, recovery, start, stats, workout


def create_bot() -> Bot:
    settings = get_settings()
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Create .env from .env.example.")
    session = AiohttpSession(proxy=settings.telegram_proxy or None)
    return Bot(token=settings.bot_token, session=session)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(workout.router)
    dp.include_router(nutrition.router)
    dp.include_router(recovery.router)
    dp.include_router(export.router)
    dp.include_router(stats.router)
    return dp
