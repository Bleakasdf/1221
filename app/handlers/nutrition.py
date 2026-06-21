from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.handlers.common import ensure_allowed
from app.keyboards import main_menu, nutrition_keyboard
from app.services.nutrition_service import grocery_basket_text, nutrition_text, post_workout_food_text


router = Router()


@router.message(Command("nutrition"))
@router.message(lambda message: message.text == "🍽 Рекомендации к питанию")
async def nutrition(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    await message.answer(nutrition_text(), reply_markup=nutrition_keyboard())


@router.message(lambda message: message.text == "Что поесть после тренировки?")
async def post_workout(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    await message.answer(post_workout_food_text(), reply_markup=nutrition_keyboard())


@router.message(lambda message: message.text == "Корзина продуктов на неделю")
async def groceries(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    await message.answer(grocery_basket_text(), reply_markup=nutrition_keyboard())


@router.message(lambda message: message.text == "Назад в меню")
async def back_to_menu(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    await message.answer("Главное меню.", reply_markup=main_menu())
