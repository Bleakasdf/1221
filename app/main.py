import asyncio

from aiogram.exceptions import TelegramNetworkError

from app.bot import create_bot, create_dispatcher
from app.database import init_db


async def main() -> None:
    init_db()
    while True:
        bot = create_bot()
        dp = create_dispatcher()
        try:
            print("Bot is starting...")
            await dp.start_polling(bot, polling_timeout=10)
        except TelegramNetworkError as error:
            print()
            print("Telegram API connection was interrupted.")
            print("Check internet, VPN, or proxy. Retrying in 5 seconds.")
            print(f"Technical error: {error}")
            print()
            await asyncio.sleep(5)
        finally:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
