from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def reply_keyboard(rows: list[list[str]], resize: bool = True) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text) for text in row] for row in rows],
        resize_keyboard=resize,
    )


def main_menu() -> ReplyKeyboardMarkup:
    return reply_keyboard([
        ["🏋️ Начать тренировку"],
        ["🍽 Рекомендации к питанию", "📊 Статистика"],
        ["📤 Выгрузить данные", "🧠 Восстановление / ОС"],
        ["⚙️ Настройки"],
    ])


def workout_types() -> ReplyKeyboardMarkup:
    return reply_keyboard([
        ["Спина / Подтягивания"],
        ["Грудь / Жим"],
        ["Калистеника / Ноги"],
        ["Своя тренировка"],
    ])


def cycle_weeks() -> ReplyKeyboardMarkup:
    return reply_keyboard([["Неделя 1", "Неделя 2"], ["Неделя 3", "Неделя 4"]])


def rpe_keyboard() -> ReplyKeyboardMarkup:
    return reply_keyboard([
        ["6 — легко", "7 — рабочий"],
        ["8 — тяжело"],
        ["9 — почти предел", "10 — максимум"],
    ])


def feedback_keyboard() -> ReplyKeyboardMarkup:
    return reply_keyboard([
        ["Всё ок", "Тяжело"],
        ["Боль / дискомфорт", "Техника плохая"],
        ["Пропустить комментарий"],
    ])


def next_exercise_keyboard() -> ReplyKeyboardMarkup:
    return reply_keyboard([["Следующее упражнение"], ["Пропустить упражнение", "Завершить тренировку"]])


def export_keyboard() -> ReplyKeyboardMarkup:
    return reply_keyboard([
        ["Выгрузить всё одним Excel"],
        ["Выгрузить тренировки Excel"],
        ["Выгрузить тренировки CSV", "Выгрузить восстановление CSV"],
        ["Назад в меню"],
    ])


def nutrition_keyboard() -> ReplyKeyboardMarkup:
    return reply_keyboard([
        ["Что поесть после тренировки?"],
        ["Корзина продуктов на неделю"],
        ["Назад в меню"],
    ])
