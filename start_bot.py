# /// script
# dependencies = [
#         "asyncio", "requests", "bs4", "deep_translator", "aiogram", "openai", "aiosqlite", "dotenv", "spacy", 
# ]
# ///

#uv run start_bot.py
import asyncio, os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import logging

from bot.keyboards import inline_keyboards, reply_keyboards
from bot.services import word_selector
from bot.handlers import callbacks, commands, user_message, payment
from bot.database import create_db, queries


logging.basicConfig(level=logging.INFO)
logging.info("Бот запущений")

words = word_selector.all_words()

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

dp.include_routers(
    inline_keyboards.router,
    reply_keyboards.router,
    callbacks.router,
    commands.router,
    user_message.router,
    payment.router
)

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
                logging.error(f"Incorrect user_id. Details: {e}. User_id = {uid}")

        await asyncio.sleep(3600)  

async def check_premium_expiry_periodically():
    """Перевіряє і знімає преміум-статус у всіх користувачів раз на годину."""
    while True:
        user_ids = await queries.all_user_ids()
        for uid in user_ids:
            await queries.deactivate_expired_premium(uid)
        await asyncio.sleep(60)

# 🚀 Головна функція
async def main():  
    asyncio.create_task(send_words_periodically())
    asyncio.create_task(check_premium_expiry_periodically())
    await dp.start_polling(bot)

if __name__ == "__main__":
    create_db.main_db()
    create_db.status_db() 
    asyncio.run(main())