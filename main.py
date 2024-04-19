import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from config import private


from middlewares.checker import DataBaseMiddleware

from database.engine import create_db, drop_db, session_maker


from handlers.main_root import main_root

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

dp.include_router(main_root)

async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()

async def on_shutdown(bot):
    print("Бот упал")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseMiddleware(session_pool=session_maker))
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())