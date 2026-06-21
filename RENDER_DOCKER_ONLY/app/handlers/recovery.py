from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.handlers.common import db_session, ensure_allowed, user_from_message
from app.keyboards import main_menu
from app.services.recovery_service import recovery_recommendation, save_recovery
from app.states import RecoveryFlow


router = Router()


@router.message(Command("recovery"))
@router.message(lambda message: message.text == "🧠 Восстановление / ОС")
async def recovery_start(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    await state.clear()
    await state.set_state(RecoveryFlow.sleep_hours)
    await message.answer("Сон, часы? Например: 7.5")


@router.message(RecoveryFlow.sleep_hours)
async def sleep_hours(message: Message, state: FSMContext) -> None:
    await _number_step(message, state, "sleep_hours", RecoveryFlow.sleep_quality, "Качество сна 1–5?")


@router.message(RecoveryFlow.sleep_quality)
async def sleep_quality(message: Message, state: FSMContext) -> None:
    await _int_1_5_step(message, state, "sleep_quality", RecoveryFlow.energy, "Энергия 1–5?")


@router.message(RecoveryFlow.energy)
async def energy(message: Message, state: FSMContext) -> None:
    await _int_1_5_step(message, state, "energy", RecoveryFlow.soreness, "Крепатура 1–5?")


@router.message(RecoveryFlow.soreness)
async def soreness(message: Message, state: FSMContext) -> None:
    await _int_1_5_step(message, state, "soreness", RecoveryFlow.stress, "Стресс 1–5?")


@router.message(RecoveryFlow.stress)
async def stress(message: Message, state: FSMContext) -> None:
    await _int_1_5_step(message, state, "stress", RecoveryFlow.lower_back_state, "Состояние поясницы 1–5?")


@router.message(RecoveryFlow.lower_back_state)
async def lower_back(message: Message, state: FSMContext) -> None:
    await _int_1_5_step(message, state, "lower_back_state", RecoveryFlow.resting_pulse, "Пульс покоя?")


@router.message(RecoveryFlow.resting_pulse)
async def resting_pulse(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    try:
        value = int(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer("Введи число. Например: 58")
        return
    await state.update_data(resting_pulse=value)
    await state.set_state(RecoveryFlow.comment)
    await message.answer("Общий комментарий? Можно написать '-'")


@router.message(RecoveryFlow.comment)
async def comment(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    await state.update_data(comment=None if message.text == "-" else message.text)
    data = await state.get_data()
    with db_session() as session:
        user = user_from_message(session, message)
        save_recovery(session, user, data)
    await state.clear()
    await message.answer(f"Восстановление сохранено.\n\n{recovery_recommendation(data)}", reply_markup=main_menu())


async def _number_step(message: Message, state: FSMContext, key: str, next_state, prompt: str) -> None:
    if not await ensure_allowed(message):
        return
    try:
        value = float(message.text.replace(",", "."))
    except (ValueError, AttributeError):
        await message.answer("Введи число. Например: 7.5")
        return
    await state.update_data(**{key: value})
    await state.set_state(next_state)
    await message.answer(prompt)


async def _int_1_5_step(message: Message, state: FSMContext, key: str, next_state, prompt: str) -> None:
    if not await ensure_allowed(message):
        return
    try:
        value = int(message.text)
    except (ValueError, AttributeError):
        await message.answer("Введи число от 1 до 5.")
        return
    if value < 1 or value > 5:
        await message.answer("Введи число от 1 до 5.")
        return
    await state.update_data(**{key: value})
    await state.set_state(next_state)
    await message.answer(prompt)
