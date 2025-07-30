import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage


from dotenv import load_dotenv

from aiohttp import web

from bot.keyboards import inline_keyboards, reply_keyboards
from bot.services import word_selector
from bot.handlers import callbacks, commands, user_message, payment
from bot.database import create_db, queries

# ────────────────────🔧 Налаштування ────────────────────────
load_dotenv()

TOKEN = os.getenv("TOKEN")

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
        await asyncio.sleep(840)

# ───────────────────🌐 Webhook FastAPI App ─────────────────────
async def web_server():
    async def handle(request):
        return web.Response(text="Bot is running")

    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    await site.start()


async def main():
    create_db.main_db()
    create_db.status_db()

    asyncio.create_task(send_words_periodically())
    asyncio.create_task(check_premium_expiry_periodically())

    await asyncio.gather(
        dp.start_polling(bot),
        web_server(),

    )

# ───────────────────── Запуск Web-сервера ──────────────────────
if __name__ == "__main__":
    asyncio.run(main())


