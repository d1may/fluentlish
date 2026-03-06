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

load_dotenv()

TOKEN = os.getenv("TOKEN")

WORD_SEND_INTERVAL = 3600
PREMIUM_CHECK_INTERVAL = 840
STARTUP_DELAY = 2
DEFAULT_PORT = 10000

logging.basicConfig(level=logging.INFO)
logging.info("Bot is starting...")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

dp.include_routers(
    inline_keyboards.router,
    reply_keyboards.router,
    callbacks.router,
    commands.router,
    user_message.router,
    payment.router,
)


async def send_words_periodically():
    await asyncio.sleep(STARTUP_DELAY)

    while True:
        user_ids = await queries.all_user_ids()

        for uid in user_ids:
            word = await word_selector.get_smart_word(uid)
            try:
                await bot.send_message(
                    uid,
                    f"🔤 Word: <b>{word}</b>",
                    reply_markup=inline_keyboards.category_kb,
                )
            except Exception as e:
                logging.error("Failed to send word: %s | User ID: %s", e, uid)

        await asyncio.sleep(WORD_SEND_INTERVAL)


async def check_premium_expiry_periodically():
    while True:
        user_ids = await queries.all_user_ids()
        for uid in user_ids:
            expired = await queries.deactivate_expired_premium(uid)
            if expired:
                try:
                    await bot.send_message(
                        uid,
                        "❌ Your premium subscription has expired. You can renew it in the menu.",
                    )
                except Exception as e:
                    logging.error("Failed to send premium expiry notice: %s", e)
        await asyncio.sleep(PREMIUM_CHECK_INTERVAL)


async def web_server():
    async def handle(request):
        return web.Response(text="Bot is running")

    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", DEFAULT_PORT)))
    await site.start()


async def main():
    create_db.main_db()
    create_db.status_db()

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(send_words_periodically())
    asyncio.create_task(check_premium_expiry_periodically())
    asyncio.create_task(web_server())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
