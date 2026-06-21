import asyncio

from aiogram.exceptions import TelegramNetworkError

from app.bot import create_bot


async def main() -> None:
    bot = create_bot()
    try:
        me = await bot.get_me()
        print(f"OK: @{me.username}")
    except TelegramNetworkError as error:
        print("Не удалось подключиться к Telegram API.")
        print("Проверь интернет, VPN или TELEGRAM_PROXY в .env.")
        print(f"Техническая ошибка: {error}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
