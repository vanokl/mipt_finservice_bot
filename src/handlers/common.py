from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.kb import make_vertial_keyboard
import sqlite3
from aiogram.fsm.state import StatesGroup, State

router = Router()

available_actions = ["Добавить доход",
                     "Добавить расход",
                     "Узнать курс валюты",
                     "Покзать отчет трат за месяц"
                     ]


class Common(StatesGroup):
    cmd_start = State()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Выберите действие",
        reply_markup=make_vertial_keyboard(available_actions)
    )

    conn = sqlite3.connect(os.environ['DB_PATH'])
    cursor = conn.cursor()
    cursor.execute(f"SELECT user_id from users where user_id={message.from_user.id}")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, username, budget, currency) VALUES (?, ?, null, 'RUB')",
                       (message.from_user.id, message.from_user.first_name))
        conn.commit()
    conn.close()



