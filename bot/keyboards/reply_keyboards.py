from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router

router = Router()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/new_word"),
            KeyboardButton(text="/definition"),
            KeyboardButton(text="/studied")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True
)
