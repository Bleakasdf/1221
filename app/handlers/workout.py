from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.data.workout_plan import WORKOUT_TYPES
from app.handlers.common import db_session, ensure_allowed, user_from_message
from app.keyboards import cycle_weeks, feedback_keyboard, main_menu, next_exercise_keyboard, rpe_keyboard, workout_types
from app.services.workout_service import (
    TYPE_BY_TITLE,
    add_exercise_log,
    create_workout_session,
    finish_workout,
    plan_for_state,
    workout_summary,
)
from app.states import WorkoutFlow


router = Router()


def _exercise_text(exercise: dict, index: int, total: int) -> str:
    return (
        f"Упражнение {index + 1} из {total}\n\n"
        f"{exercise['name']}\n"
        f"Блок: {exercise['section']}\n\n"
        f"План:\n{exercise['plan']}\n\n"
        "Введи факт выполнения.\n"
        "Примеры:\n"
        "+5 кг: 5,5,5,5,5\n"
        "85 кг: 5,5,5,4,4\n"
        "без веса: 12,10,9\n"
        "30 сек, 25 сек, 20 сек"
    )


async def _show_current_exercise(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    plan = data["plan"]
    index = data["exercise_index"]
    await state.set_state(WorkoutFlow.entering_actual)
    await message.answer(_exercise_text(plan[index], index, len(plan)))


@router.message(Command("workout"))
@router.message(lambda message: message.text == "🏋️ Начать тренировку")
async def start_workout(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    await state.clear()
    await state.set_state(WorkoutFlow.choosing_type)
    await message.answer("Какую тренировку делаем сегодня?", reply_markup=workout_types())


@router.message(WorkoutFlow.choosing_type)
async def choose_type(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    if message.text == "Своя тренировка":
        await message.answer("Своя тренировка будет в следующей версии. Пока выбери один из трёх дней.", reply_markup=workout_types())
        return
    workout_type = TYPE_BY_TITLE.get(message.text)
    if not workout_type:
        await message.answer("Выбери тренировку кнопкой.", reply_markup=workout_types())
        return
    await state.update_data(workout_type=workout_type, workout_title=WORKOUT_TYPES[workout_type])
    await state.set_state(WorkoutFlow.choosing_week)
    await message.answer("Какая сейчас неделя цикла?", reply_markup=cycle_weeks())


@router.message(WorkoutFlow.choosing_week)
async def choose_week(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    if not message.text or not message.text.startswith("Неделя "):
        await message.answer("Выбери неделю кнопкой.", reply_markup=cycle_weeks())
        return
    cycle_week = int(message.text.split()[-1])
    data = await state.get_data()
    plan = plan_for_state(data["workout_type"], cycle_week)
    with db_session() as session:
        user = user_from_message(session, message)
        workout = create_workout_session(session, user, data["workout_title"], cycle_week)
    await state.update_data(session_id=workout.id, cycle_week=cycle_week, plan=plan, exercise_index=0)
    await _show_current_exercise(message, state)


@router.message(WorkoutFlow.entering_actual)
async def enter_actual(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Не понял формат. Пример: 85 кг: 5,5,5,4,4")
        return
    await state.update_data(actual_value=message.text.strip())
    await state.set_state(WorkoutFlow.choosing_rpe)
    await message.answer("Насколько тяжело было?", reply_markup=rpe_keyboard())


@router.message(WorkoutFlow.choosing_rpe)
async def choose_rpe(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    try:
        rpe = int(message.text.split()[0])
    except (ValueError, AttributeError):
        rpe = 0
    if rpe < 1 or rpe > 10:
        await message.answer("Выбери RPE кнопкой или введи число от 1 до 10.", reply_markup=rpe_keyboard())
        return
    await state.update_data(rpe=rpe)
    await state.set_state(WorkoutFlow.entering_comment)
    await message.answer("Комментарий по упражнению?", reply_markup=feedback_keyboard())


@router.message(WorkoutFlow.entering_comment)
async def enter_comment(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    data = await state.get_data()
    exercise = data["plan"][data["exercise_index"]]
    comment = message.text.strip() if message.text else "Пропустить комментарий"
    with db_session() as session:
        add_exercise_log(session, data["session_id"], exercise, data["actual_value"], data["rpe"], comment)
    await state.set_state(WorkoutFlow.after_exercise)
    await message.answer("Сохранено.", reply_markup=next_exercise_keyboard())


@router.message(WorkoutFlow.after_exercise)
async def after_exercise(message: Message, state: FSMContext) -> None:
    if not await ensure_allowed(message):
        return
    data = await state.get_data()
    if message.text == "Пропустить упражнение":
        exercise = data["plan"][data["exercise_index"]]
        with db_session() as session:
            add_exercise_log(session, data["session_id"], exercise, "skipped", None, "Пропущено", status="skipped")
        data["exercise_index"] += 1
    elif message.text == "Завершить тренировку":
        await _finish(message, state)
        return
    else:
        data["exercise_index"] += 1

    if data["exercise_index"] >= len(data["plan"]):
        await state.update_data(exercise_index=data["exercise_index"])
        await _finish(message, state)
        return
    await state.update_data(exercise_index=data["exercise_index"])
    await _show_current_exercise(message, state)


async def _finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    with db_session() as session:
        finish_workout(session, data["session_id"])
        summary = workout_summary(session, data["session_id"])
    await state.clear()
    await message.answer(
        f"Тренировка сохранена.\n\n{summary}\n\n"
        "Можно заполнить восстановление через /recovery.",
        reply_markup=main_menu(),
    )
