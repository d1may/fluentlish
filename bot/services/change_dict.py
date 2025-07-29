from bot.database import queries

def clamp_rating(rating: int) -> int:
    return max(1, min(rating, 10))

async def set_dict(user_id: int, user_word: str, word_status: str):
        row = await queries.select_rating(user_id, user_word)

        base_rating = 5

        # 2. Зміна рейтингу залежно від відповіді
        if word_status == "easy":
            rating_change = 2
        elif word_status == "hard":
            rating_change = -3
        else:
            rating_change = 0

        if row:
            current_rating = row[1]
            new_rating = clamp_rating(current_rating + rating_change)
            await queries.update_rating(new_rating, user_id, user_word)

        else:
            await queries.insert_rating(user_id, user_word, base_rating)
