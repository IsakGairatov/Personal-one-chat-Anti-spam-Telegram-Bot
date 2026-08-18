import asyncio
import os
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN

from handlers.include_bot_routers import router


async def main():

    bot = Bot(BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())