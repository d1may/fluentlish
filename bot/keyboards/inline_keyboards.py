from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router

router = Router()

category_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Too easy", callback_data="easy"),
        InlineKeyboardButton(text="Ok", callback_data="ok"),
        InlineKeyboardButton(text="Too hard", callback_data="hard"),
        InlineKeyboardButton(text="Definition", callback_data="definition")
    ]
])

practice_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Practice", callback_data="practice"),
        InlineKeyboardButton(text="No practice", callback_data="no_practice"),
    ]
])

studied_practice_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Practice", callback_data="s_practice"),
        InlineKeyboardButton(text="No practice", callback_data="no_practice"),
    ]
])

payment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="1 day", callback_data="10"),
        InlineKeyboardButton(text="1 month", callback_data="120"),
        InlineKeyboardButton(text="6 month", callback_data="500"),
    ]
])