from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.handlers.common import db_session, ensure_allowed, user_from_message
from app.keyboards import main_menu


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    with db_session() as session:
        user_from_message(session, message)
    await message.answer("Готов вести тренировку. Выбирай действие:", reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    await message.answer(
        "/workout — начать тренировку\n"
        "/nutrition — питание\n"
        "/recovery — восстановление\n"
        "/export — выгрузка\n"
        "/stats — статистика\n"
        "/settings — настройки\n"
        "/cancel — отменить текущее действие",
        reply_markup=main_menu(),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    await state.clear()
    await message.answer("Ок, текущий сценарий отменён.", reply_markup=main_menu())


@router.message(Command("settings"))
@router.message(lambda message: message.text == "⚙️ Настройки")
async def settings(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    with db_session() as session:
        user = user_from_message(session, message)
        await message.answer(
            "Настройки MVP:\n"
            f"Рост: {user.height_cm or 183} см\n"
            f"Вес: {user.weight_kg or 82} кг\n"
            f"Цель: набор до {user.target_weight_kg or 89} кг\n"
            "Калории: 2950\nБелок: 160 г\nЖиры: 80 г\nУглеводы: 400 г",
            reply_markup=main_menu(),
        )
