from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
import requests
from keyboards.kb import make_vertial_keyboard
from handlers.common import Common, available_actions

router = Router()

available_curr_code = ["USD", "EUR"]


class GetCurrency(StatesGroup):
    get_currency_code = State()
    show_currency_rate = State()


async def get_currency_rate(currency_code):
    url = f"https://www.cbr-xml-daily.ru/latest.js"  # API Центробанка
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if currency_code in data['rates']:
            return 1 / float(data['rates'][currency_code])
        else:
            return None
    else:
        return None


@router.message(F.text.lower() == "узнать курс валюты")
async def currency_handler(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите вылюту",
        reply_markup=make_vertial_keyboard(available_curr_code)
    )
    await state.set_state(GetCurrency.show_currency_rate)

@router.message(GetCurrency.show_currency_rate, F.text)
async def show_currency_rate(message: Message, state: FSMContext):
    from handlers.common import Common
    rate = await get_currency_rate(message.text)

    if rate:
        await message.reply(f"Курс {message.text} к рублю: {rate:.2f} ₽", reply_markup=make_vertial_keyboard(available_actions))
    else:
        await message.reply(f"Не удалось получить курс валюты {message.text}. Попробуйте позже.")

    await state.set_state(Common.cmd_start)
    await message.answer(
        text="Выберите действие",
        reply_markup=make_vertial_keyboard(available_actions)
    )

