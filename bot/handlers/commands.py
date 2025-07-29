from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import StatesGroup, State
from random import choice, shuffle 
import csv

from bot.keyboards import reply_keyboards, inline_keyboards
from bot.services import parser_cambridge
from bot.database import queries

router = Router()

SONG = types.input_file.FSInputFile("bot/resources/knock.ogg")
ABRAMS = types.input_file.FSInputFile("bot/resources/abrams.jpg")

words = []

with open('bot/data/oxford-3000.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    for row in reader:
        word = row[0]
        words.append(word)

class DfState(StatesGroup):
    waiting_for_word = State()

@router.message(CommandStart())
async def command_start_handler(message: types.Message):
    print(message.chat.id)
    user_id = message.from_user.id

    await message.answer(f"🇺🇸 knock knock...\nHi {message.from_user.first_name} , I'm your English learning bot. I will send you one English word every hour, I will try to match the words to your level and encourage you to learn the language.")
    
    exists = await queries.check_user_id(user_id)
    if not exists:
        word = choice(words)
        await message.answer(f"🔤 Word: <b>{word}</b>", reply_markup=inline_keyboards.category_kb)

@router.message(Command("new_word"))
async def get_new_word(message: types.Message):
    new_word = choice(words)
    await message.answer(f"🔤 Word: <b>{new_word}</b>", reply_markup=inline_keyboards.category_kb)
    
@router.message(Command("definition"))
async def start_df(message: types.Message, state: FSMContext):
    await message.answer("Please enter a word")
    await state.set_state(DfState.waiting_for_word)

@router.message(Command("profile"))
async def user_profile(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    joined = await queries.select_oldest_date(user_id)
    vocab_count = await queries.select_all_words(user_id)
    is_premium = await queries.check_is_premium(user_id)
    status_text = ""
    if is_premium == 1:
        # Отримати дату закінчення
        db = await queries.get_db_connection()
        async with db.execute("SELECT end_date FROM vip WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
        await db.close()
        end_date = row["end_date"] if row else None
        status_text = f"<b>👑 Premium:</b> ✅\n⏳ Active until: <code>{end_date}</code>"
    else:
        status_text = "<b>😐 Status:</b> Standard user"
    await message.answer(f"""
📊 Your Profile

👤 Username: @{username}
🆔 ID: {user_id}
📅 Joined: {joined}
📖 Your vocabulary: {vocab_count}
{status_text}
""")

    
@router.message(DfState.waiting_for_word)
async def handle_df(message: types.Message, state: FSMContext):
    try:
        result = await parser_cambridge.get_cambridge_data(message.text)
        if result:
            text = (
                f"📘 <b>Word:</b> <code>{result['word'].upper()}</code>\n"
                f"🧩 <b>Part of Speech:</b> {result['part_of_speech']}\n"
                f"🔊 <b>UK:</b> {result['ipa_uk']} | <b>US:</b> {result['ipa_us']}\n"
                f"🎯 <b>Level:</b> {result['level']}\n\n"
                f"🧠 <b>Definition:</b> <code>{result['definition']}</code>\n"
                f"🧾 <b>Example 1:</b> {result['examples'][0] if result['examples'] else '—'}\n"
                f"🧾 <b>Example 2:</b> {result['examples'][1] if len(result['examples']) > 1 else '—'}\n\n"
            )
            await message.answer(text)
        else:
            await message.answer("❌ Data could not be found. Please try again.")
    except Exception:
        await message.answer("❌ Data could not be found. Please try again.")
    finally:
        await state.clear()
    
@router.message(Command("studied"))
async def get_studied_words(message: types.Message):
    user_id = message.from_user.id
    words = await queries.select_studied_from_db(user_id)
    shuffle(words)

    if not words:
        await message.answer("You don't yet have any words with a level of 8 or higher.")
        return

    text = "\n".join([f"{i}. {word}" for i, word in enumerate(words, 1)])
    await message.answer(f"List of studied words:\n\n{text}", reply_markup=inline_keyboards.studied_practice_kb)

@router.message(Command("my_words"))
async def show_all_words(message: types.Message):
    words = await queries.get_all_words(message.from_user.id)
    if not words:
        await message.answer("Your dictionary is empty.")
        return
    text = "\n".join([f"{i}. {word}" for i, word in enumerate(words, 1)])
    await message.answer(f"Your words:\n\n{text}\n\nTo delete a word, use /del_word 'word'\nTo add a word, use /add_word 'word'")

@router.message(Command("del_word"))
async def delete_word(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Please provide the word to delete. Example: /del_word apple")
        return
    word_to_delete = args[1].strip()
    await queries.delete_word(user_id, word_to_delete)
    await message.answer(f"Word '{word_to_delete}' has been deleted from your dictionary.")

@router.message(Command("add_word"))
async def add_word(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Please provide the word to add. Example: /add_word apple")
        return
    word_to_add = args[1].strip()
    add_message = await queries.add_word(user_id, word_to_add)
    await message.answer(add_message)

