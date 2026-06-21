from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from app.handlers.common import db_session, ensure_allowed, user_from_message
from app.keyboards import export_keyboard, main_menu
from app.services.export_service import export_all_excel, export_recovery_csv, export_workouts_csv


router = Router()


@router.message(Command("export"))
@router.message(lambda message: message.text == "📤 Выгрузить данные")
async def export_menu(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    await message.answer("Что выгрузить?", reply_markup=export_keyboard())


@router.message(lambda message: message.text in {
    "Выгрузить всё одним Excel",
    "Выгрузить тренировки Excel",
    "Выгрузить тренировки CSV",
    "Выгрузить восстановление CSV",
})
async def export_file(message: Message) -> None:
    if not await ensure_allowed(message):
        return
    try:
        with db_session() as session:
            user = user_from_message(session, message)
            if message.text in {"Выгрузить всё одним Excel", "Выгрузить тренировки Excel"}:
                path = export_all_excel(session, user)
            elif message.text == "Выгрузить тренировки CSV":
                path = export_workouts_csv(session, user)
            else:
                path = export_recovery_csv(session, user)
        await message.answer_document(FSInputFile(path), caption="Готово.", reply_markup=main_menu())
    except ValueError as error:
        await message.answer(str(error), reply_markup=main_menu())
    except Exception as error:
        await message.answer(f"Не получилось создать экспорт: {error}", reply_markup=main_menu())
