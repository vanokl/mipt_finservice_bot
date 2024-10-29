from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.kb import make_vertial_keyboard
import sqlite3
from handlers.common import Common, available_actions
import os

router = Router()

class GetReport(StatesGroup):
    get_report = State()


async def get_report():
    conn = sqlite3.connect(os.environ['DB_PATH'])
    cursor = conn.cursor()
    cursor.execute("select sum(amount) from transactions where amount < 0 and date >= DATE('now', 'start of month');")
    expense = cursor.fetchone()[0]
    cursor.execute("select sum(amount) from transactions where amount > 0 and date >= DATE('now', 'start of month');")
    income = cursor.fetchone()[0]
    conn.close()
    return expense, income

@router.message(F.text.lower() == "покзать отчет трат за месяц")
async def result_show(message: Message, state: FSMContext):
    from handlers.common import Common

    expense, income = await get_report()
    await message.answer(
        text=f"Отчет за текущий месяц\n    Расходы: {expense}\n    Доходы: {income}"
    )
    await state.set_state(Common.cmd_start)
    await message.answer(
        text="Выберите действие",
        reply_markup=make_vertial_keyboard(available_actions)
    )
