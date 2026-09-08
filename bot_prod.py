import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

from config import BOT_TOKEN
from handlers.include_bot_routers import router


WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my_secret")
WEBHOOK_PATH = "/webhook"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)


async def on_startup(bot: Bot):
    base_url = os.getenv("RENDER_EXTERNAL_URL")

    await bot.set_webhook(
        url=f"{base_url}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
    )


async def on_shutdown(bot: Bot):
    print("SHUTDOWN CALLED", flush=True)


dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)


app = web.Application()

SimpleRequestHandler(
    dispatcher=dp,
    bot=bot,
    secret_token=WEBHOOK_SECRET,
).register(
    app,
    path=WEBHOOK_PATH,
)

setup_application(app, dp, bot=bot)


web.run_app(
    app,
    host="0.0.0.0",
    port=int(os.getenv("PORT", "10000")),
)