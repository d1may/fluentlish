from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from bot.services import change_dict, parser_cambridge
from bot.keyboards import inline_keyboards
from bot.handlers import user_message, payment
from bot.database import queries

router = Router()

@router.callback_query(lambda c: c.data in ["10", "120", "500"])
async def plan_payment(callback: types.CallbackQuery):
    await payment.start_payment(callback.message, int(callback.data))
    await callback.answer()


@router.callback_query()

async def func_with_word(callback: types.CallbackQuery, state: FSMContext):        
    user_id = callback.from_user.id
    word = " ".join(callback.message.text.split()[2:])
    last_word = await queries.select_last_word(user_id)
    data = callback.data

    if data in ["ok", "hard", "easy"]:
        await change_dict.set_dict(user_id=user_id, user_word=word, word_status=data)
        await callback.message.delete()
        
        if data == "ok":
            await callback.message.answer(f"🟡Okay, this word <code>“{word}”</code> is not too difficult")
            
        elif data == "easy":
            await callback.message.answer(f"🟢This word <code>{word}</code> is very easy.", reply_markup=inline_keyboards.practice_kb)
            
        else:
            await callback.message.answer(f"🔴Well, this word <code>“{word}”</code> turned out to be too difficult")

    elif data == "practice":
        last_word = callback.message.text.split()[2]
        await for_practice(callback, state, last_word)

    elif data == "s_practice":
        last_word = callback.message.text.split()[-1]
        await for_practice(callback, state, last_word)

    elif data == "no_practice":
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.clear()                                 
    
    elif data == "definition":
        result = await parser_cambridge.get_cambridge_data(word)
        if result:
            text = (
                f"📘 <b>Word:</b> <code>{result['word'].upper()}</code>\n"
                f"🧩 <b>Part of Speech:</b> {result['part_of_speech']}\n"
                f"🔊 <b>UK:</b> {result['ipa_uk']} | <b>US:</b> {result['ipa_us']}\n"
                f"🎯 <b>Level:</b> {result['level']}\n\n"
                f"🧠 <b>Definition:</b> <code>{result['definition']}</code>\n"
                f"🧾 <b>Example 1:</b> {result['examples'][0] if result['examples'] else '—'}\n"
                f"🧾 <b>Example 2:</b> {result['examples'][1] if len(result['examples']) > 1 else '—'}\n"
                f"🧠 <b>Tranlation:</b> <tg-spoiler>{result['translation']}</tg-spoiler>\n\n"
            )
            await callback.message.answer(text)
        else:
            await callback.message.answer("❌ Не вдалося знайти дані. Спробуй ще раз.")
            await state.clear()

    await callback.answer()

async def for_practice(callback, state, last_word):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"✍️ Enter a sentence with <code>{last_word}</code>"
    )
    await state.set_state(user_message.User_Sentence.waiting_for_sentence)
    await state.update_data(target=last_word)