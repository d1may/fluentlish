import csv
import random
from pathlib import Path

from bot.database import queries

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OXFORD_CSV = DATA_DIR / "oxford-3000.csv"

_cached_words: list[str] | None = None


def all_words() -> list[str]:
    global _cached_words
    if _cached_words is not None:
        return _cached_words

    words = []
    with open(OXFORD_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            words.append(row[0])
    _cached_words = words
    return words


async def get_smart_word(user_id):
    db_words = await queries.select_word(user_id)

    if len(db_words) < 10:
        existing_set = set(db_words)
        all_set = set(all_words())
        unused_words = list(all_set - existing_set)
        random.shuffle(unused_words)
        needed = 10 - len(db_words)
        db_words += unused_words[:needed]

    word = random.choice(db_words)
    await queries.update_last_seen_db(user_id, word)
    return word
