import aiosqlite
from datetime import datetime, timedelta

DB_PATH = "dict.db"

async def get_db_connection():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def all_user_ids():
    db = await get_db_connection()
    async with db.execute("SELECT DISTINCT user_id FROM dictionary") as cursor:
        return [row[0] async for row in cursor]


async def check_user_id(user_id):
    db = await get_db_connection()
    async with db.execute("SELECT 1 FROM dictionary WHERE user_id = ? LIMIT 1", (user_id,)) as cursor:
        exists = await cursor.fetchone()
    return exists

async def select_studied_from_db(user_id):
    db = await get_db_connection()
    async with db.execute("SELECT word FROM dictionary WHERE user_id = ? AND rating >= 8", (user_id,)) as cursor:
        rows = await cursor.fetchall()
    return [row[0] for row in rows]

async def select_word(user_id):
    db = await get_db_connection()
    async with db.execute("SELECT AVG(rating) FROM dictionary WHERE user_id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
        avg_rating = row[0] if row[0] is not None else 0

    if avg_rating < 4:
        sql = "SELECT word FROM dictionary WHERE user_id = ? AND rating >= ? ORDER BY COALESCE(last_seen, '2000-01-01') ASC LIMIT 10"
        params = (user_id, 6)
    elif avg_rating > 7:
        sql = "SELECT word FROM dictionary WHERE user_id = ? AND rating <= ? ORDER BY COALESCE(last_seen, '2000-01-01') ASC LIMIT 10"
        params = (user_id, 3)
    else:
        sql = "SELECT word FROM dictionary WHERE user_id = ? AND rating >= ? ORDER BY COALESCE(last_seen, '2000-01-01') ASC LIMIT 10"
        params = (user_id, 4)

    async with db.execute(sql, params) as cursor:
        db_words = [row[0] async for row in cursor]
    return db_words

async def update_last_seen_db(user_id, word):
    db = await get_db_connection()
    await db.execute("""UPDATE dictionary SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ? AND word = ?""", (user_id, word))
    await db.commit()
    await db.close()


async def select_rating(user_id, user_word):
    db = await get_db_connection()
    async with db.execute("SELECT word, rating FROM dictionary WHERE user_id = ? AND word = ?", (user_id, user_word)) as cursor:
        row = await cursor.fetchone()
    return row

async def update_rating(new_rating, user_id, user_word):
    db = await get_db_connection()
    await db.execute("""UPDATE dictionary SET rating = ?, last_seen = CURRENT_TIMESTAMP WHERE user_id = ? AND word = ?""", (new_rating, user_id, user_word))
    await db.commit()
    await db.close()

async def insert_rating(user_id, user_word, base_rating):
    db = await get_db_connection()
    await db.execute("""INSERT OR IGNORE INTO dictionary (user_id, word, rating, last_seen) VALUES (?, ?, ?, CURRENT_TIMESTAMP)""", (user_id, user_word, base_rating))
    await db.commit()
    await db.close()
    
async def select_last_word(user_id):
    db = await get_db_connection()
    async with db.execute("SELECT word FROM dictionary WHERE user_id = ? ORDER BY last_seen DESC LIMIT 1",(user_id,)) as cursor:
        row = await cursor.fetchone()
    return row["word"] if row else None

async def select_oldest_date(user_id):
    db = await get_db_connection()
    async with db.execute("SELECT last_seen FROM dictionary WHERE user_id = ? ORDER BY last_seen ASC LIMIT 1",(user_id,)) as cursor:
        row = await cursor.fetchone()
    return row["last_seen"] if row else None

async def select_all_words(user_id):
    db = await get_db_connection()
    async with db.execute("SELECT COUNT(*) AS count FROM dictionary WHERE user_id = ?",(user_id,)) as cursor:
        row = await cursor.fetchone()
    return row["count"] if row else 0

async def insert_premium(user_id: int, duration_days: int):
    db = await get_db_connection()
    start = datetime.now()
    end = start + timedelta(days=duration_days)
    await db.execute("""
    INSERT INTO vip (user_id, isPremium, start_date, end_date)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        isPremium = excluded.isPremium,
        start_date = excluded.start_date,
        end_date = excluded.end_date
    """, (
        user_id,
        1,
        start.isoformat(),  # або start.strftime('%Y-%m-%d %H:%M:%S')
        end.isoformat()
    ))
    await db.commit()
    await db.close()

async def check_is_premium(user_id: int):
    """Перевіряє статус isPremium для користувача у таблиці vip."""
    db = await get_db_connection()
    async with db.execute("SELECT isPremium FROM vip WHERE user_id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
    return row["isPremium"] if row else 0

async def deactivate_expired_premium(user_id: int):
    """Знімає преміум, якщо термін дії підписки закінчився."""
    db = await get_db_connection()
    async with db.execute("SELECT end_date FROM vip WHERE user_id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
    if row:
        end_date = row["end_date"]
        if end_date and datetime.fromisoformat(end_date) < datetime.now():
            await db.execute("DELETE FROM vip WHERE user_id = ?", (user_id,))
            await db.commit()
            import logging
            logging.info(f"Преміум статус знято для user_id={user_id} (end_date={end_date})")
            # Надіслати повідомлення користувачу
            try:
                from aiogram import Bot
                from aiogram.client.default import DefaultBotProperties
                from aiogram.enums import ParseMode
                import os
                from dotenv import load_dotenv
                load_dotenv()
                TOKEN = os.getenv("TOKEN")
                bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
                await bot.send_message(user_id, "❌ Ваша преміум-підписка закінчилася. Ви можете продовжити її у меню.")
            except Exception as e:
                logging.error(f"Не вдалося надіслати повідомлення про закінчення преміум: {e}")
    await db.close()

async def get_all_words(user_id):
    """Отримує всі слова користувача з бази даних."""
    db = await get_db_connection()
    async with db.execute("SELECT word FROM dictionary WHERE user_id = ? ORDER BY word ASC", (user_id,)) as cursor:
        words = [row["word"] async for row in cursor]
        return words
async def delete_word(user_id, word_to_delete):
    """Видаляє слово з бази даних для конкретного користувача."""
    db = await get_db_connection()
    await db.execute("DELETE FROM dictionary WHERE user_id = ? AND word = ?", (user_id, word_to_delete))
    await db.commit()
    await db.close()

async def add_word(user_id, word_to_add):    
    """Додає слово до бази даних для конкретного користувача."""
    db = await get_db_connection()
    async with db.execute("SELECT 1 FROM dictionary WHERE user_id = ? AND word = ?", (user_id, word_to_add,)) as cursor:
        exists = await cursor.fetchone()
    if exists:
        print(exists)
        return "Word already exists in your dictionary."
    else:
        await db.execute("INSERT INTO dictionary (user_id, word, rating, last_seen) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (user_id, word_to_add, 5))
        await db.commit()
        await db.close()
        return "Word added successfully."


