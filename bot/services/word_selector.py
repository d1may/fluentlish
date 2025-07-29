import csv, random
from bot.database import queries


def all_words():
    
    words = []

    with open('bot/data/oxford-3000.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            word = row[0]
            words.append((word))
            
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