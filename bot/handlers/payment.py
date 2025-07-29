
from aiogram import Router, types, F
from aiogram.filters import Command
from bot.keyboards import inline_keyboards
from bot.database import queries

router = Router()

@router.message(Command("payment"))
async def choose_payment(message: types.Message):
    text = (
        "🌟 Choose your Premium plan:\n"
        "• 1 day – 10 ⭐️\n"
        "• 1 month – 120 ⭐️\n"
        "• 6 months – 500 ⭐️"
    )
    await message.answer(text, reply_markup=inline_keyboards.payment_kb)  

async def start_payment(message: types.Message, cost):
    prices = [types.LabeledPrice(label="Premium", amount=cost)]  
    await message.answer_invoice(
        title="Premium",
        description = """🚫 No ads                                                             
🤖 ChatGPT 4.1                                                             
📖 Personal dictionary                                                             
✨Full access!""",
        prices=prices,
        currency="XTR",
        provider_token=None,  
        payload="buy_premium"
    )

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery):  
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def success_payment_handler(message: types.Message):  

    payment = message.successful_payment
    amount = payment.total_amount  # у найменших одиницях, наприклад, копійках або "мілі-зірках"

    user_id = message.from_user.id

    if amount == 1:
        duration = 1
    elif amount == 120:
        duration = 30
    else:
        duration = 180

    await queries.insert_premium(user_id, duration)

    

    await message.answer(text="Thanks for your purchase!🤗", message_effect_id="5159385139981059251")

@router.message(Command("paysupport"))
async def pay_support_handler(message: types.Message):  
    await message.answer("Attention: No refunds are possible after purchase!")
    
