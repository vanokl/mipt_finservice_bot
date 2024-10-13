
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:

    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


def make_vertial_keyboard(items: list[str]) -> ReplyKeyboardMarkup:

    vertical = []
    for item in items:
        vertical.append([KeyboardButton(text=item)])
    return ReplyKeyboardMarkup(keyboard=vertical)