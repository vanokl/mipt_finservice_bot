import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from utils import db_start
from handlers import common, add_income_expense, get_currency, get_report


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    await db_start()


    API_TOKEN = os.environ['API_TOKEN']
    if not API_TOKEN:
        raise ValueError(f"env var API_TOKEN is not set")

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(API_TOKEN)

    dp.include_router(common.router)
    dp.include_router(add_income_expense.router)
    dp.include_router(get_currency.router)
    dp.include_router(get_report.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())