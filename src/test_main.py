import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import sqlite3
from handlers.add_income_expense import insert_in_db
from handlers.get_currency import get_currency_rate
from handlers.get_report import get_report
import warnings

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test_func(self, *args, **kwargs)
    return do_test

class TestDatabaseFunctions(unittest.TestCase):

    @ignore_warnings
    async def get_user_amount(self, user_id):

        conn = sqlite3.connect('app_data/finance_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            "select amount from transactions where user = 12345 and description = 'Оплата за услуги';")
        amount = cursor.fetchone()[0]

        conn.close()
        return amount

    @patch('sqlite3.connect')
    @ignore_warnings
    async def test_insert_in_db(self, mock_connect):
        # Создаем мок для соединения и курсора
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        user_id = 123456
        amount = -100.0
        user_data = "Оплата за услуги"

        await insert_in_db(user_id, amount, user_data)

        # Проверяем, что метод execute был вызван с правильными параметрами
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO transactions (user_id, amount, date, description) VALUES (?, ?, CURRENT_TIMESTAMP, ?)",
            (user_id, amount, user_data)
        )
        # Проверяем, что commit был вызван
        mock_conn.commit.assert_called_once()
        # Проверяем, что соединение было закрыто
        mock_conn.close.assert_called_once()

        # Проверяем, что сходятся значения траты
        db_amount = await self.get_user_amount(user_id)
        self.assertEqual(amount, db_amount)



    @patch('requests.get')
    @ignore_warnings
    async def test_get_currency_rate_success(self, mock_get):
        # Создаем мок ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {
                'USD': 75.0,
                'EUR': 85.0,
            }
        }
        mock_get.return_value = mock_response

        currency_code = 'USD'
        rate = await get_currency_rate(currency_code)

        # Проверяем, что функция вернула  правильный курс
        self.assertEqual(rate, 1 / 75.0)

    @patch('requests.get')
    @ignore_warnings
    async def test_get_currency_rate_not_found(self, mock_get):
        # Создаем мок ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'rates': {
                'USD': 75.0,
            }
        }
        mock_get.return_value = mock_response

        currency_code = 'GBP'  # Не существующий код валюты
        rate = await get_currency_rate(currency_code)

        # Проверяем, что функция вернула None
        self.assertIsNone(rate)

    @patch('sqlite3.connect')
    @ignore_warnings
    async def test_get_report(self, mock_connect):
        # Создаем мок для соединения и курсора
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Мокаем возвращаемые значения для запросов
        mock_cursor.fetchone.side_effect = [(200.0,), (-150.0,)]

        # Получаем отчет
        expense, income = await get_report()

        # Проверяем, что сумма расходов и доходов возвращается корректно
        self.assertEqual(expense, -150.0)
        self.assertEqual(income, 200.0)

        # Проверяем, что запросы были выполнены
        mock_cursor.execute.assert_any_call(
            "select sum(amount) from transactions where amount < 0 and date >= DATE('now', 'start of month');"
        )
        mock_cursor.execute.assert_any_call(
            "select sum(amount) from transactions where amount > 0 and date >= DATE('now', 'start of month');"
        )

        # Проверяем, что соединение было закрыто
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    # Запускаем цикл событий для выполнения асинхронного теста
    asyncio.run(unittest.main())
