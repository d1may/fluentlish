from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.services import check_sentence
from bot.database import queries
from bot.services import gpt

router = Router()

class User_Sentence(StatesGroup):
    waiting_for_sentence = State()  

@router.message(User_Sentence.waiting_for_sentence)
async def user_sentence_with_word(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target = data.get("target")
    await message.answer("Bot checks your sentence...")
    user_id = message.from_user.id
    is_premium = await queries.check_is_premium(user_id)
    if is_premium == 1:
        result = gpt.check_sentence(target, message.text)
    else:
        result = check_sentence.sentence_contains_word(target, message.text)
    await message.answer(result)
    await state.clear()