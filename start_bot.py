import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from dotenv import load_dotenv

from aiohttp import web

from bot.keyboards import inline_keyboards, reply_keyboards
from bot.services import word_selector
from bot.handlers import callbacks, commands, user_message, payment
from bot.database import create_db, queries

# ────────────────────🔧 Налаштування ────────────────────────
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # приклад: https://fluentlishbot.onrender.com/webhook

logging.basicConfig(level=logging.INFO)
logging.info("Бот запускається...")

# ────────────────────🤖 Ініціалізація ────────────────────────
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(
    inline_keyboards.router,
    reply_keyboards.router,
    callbacks.router,
    commands.router,
    user_message.router,
    payment.router
)

# ───────────────────📨 Автоматичне надсилання слів ─────────────
async def send_words_periodically():
    await asyncio.sleep(2)

    while True:
        user_ids = await queries.all_user_ids()

        for uid in user_ids:
            word = await word_selector.get_smart_word(uid)
            try:
                await bot.send_message(
                    uid,
                    f"🔤 Word: <b>{word}</b>",
                    reply_markup=inline_keyboards.category_kb
                )
            except Exception as e:
                logging.error(f"❌ Помилка надсилання: {e} | User ID: {uid}")

        await asyncio.sleep(3600)

async def check_premium_expiry_periodically():
    while True:
        user_ids = await queries.all_user_ids()
        for uid in user_ids:
            await queries.deactivate_expired_premium(uid)
        await asyncio.sleep(60)

# ───────────────────🌐 Webhook FastAPI App ─────────────────────
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    create_db.main_db()
    create_db.status_db()

    asyncio.create_task(send_words_periodically())
    asyncio.create_task(check_premium_expiry_periodically())

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")

    setup_application(app, dp, bot=bot, on_startup=on_startup, on_shutdown=on_shutdown)
    return app

# ───────────────────── Запуск Web-сервера ──────────────────────
if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
