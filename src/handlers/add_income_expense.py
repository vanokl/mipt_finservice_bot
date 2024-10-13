from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.kb import make_vertial_keyboard
import sqlite3
from handlers.common import Common, available_actions


router = Router()

available_actions = ["Добавить доход",
                     "Добавить расход",
                     "Узнать курс валюты",
                     "Покзать отчет трат за месяц"
                     ]


class AddIncomeExpense(StatesGroup):
    set_value = State()
    set_description = State()
    result = State()


@router.message(F.text.lower().in_({"добавить расход", "добавить доход"}) )
async def value_set(message: Message, state: FSMContext):
    await message.answer(
        text="Укажите сумму:"
    )
    await state.update_data(trx_type=message.text.lower())
    await state.set_state(AddIncomeExpense.set_description)


@router.message(AddIncomeExpense.set_description, F.text)
async def description_set(message: Message, state: FSMContext):
    await message.answer(
        text="Добавьте описание:"
    )
    await state.update_data(amount=message.text.lower())
    await state.set_state(AddIncomeExpense.result)


@router.message(AddIncomeExpense.result, F.text)
async def result_show(message: Message, state: FSMContext):
    await state.update_data(description=message.text.lower())
    user_data = await state.get_data()

    if user_data["trx_type"] == "добавить расход" and "-" not in user_data["amount"]:
        user_data["amount"] = "-" + user_data["amount"]

    await message.answer(
        text="Запись добавлена"
    )
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, amount, date, description) VALUES (?, ?, CURRENT_TIMESTAMP, ?)",
                   (message.from_user.id, float(user_data['amount']), user_data['description'] ))
    conn.commit()
    conn.close()
    await state.set_state(Common.cmd_start)
    await message.answer(
        text="Выберите действие",
        reply_markup=make_vertial_keyboard(available_actions)
    )
