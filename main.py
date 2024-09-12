# Основной файл бота


# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv
from asyncio import run
from aiogram import Bot, Dispatcher


# Подключение пользовательских модулей
from bot import bot
from handlers.service_handlers import service_router
from handlers.config_handlers import config_router
from handlers.work_handlers import work_router
from handlers.incorrect_messages_handler import incorrect_router
from database.models import create_models


# Основная функция для начала работы бота
async def main() -> None:
    load_dotenv()
    await create_models()

    dp = Dispatcher()
    dp.include_routers(service_router, config_router, work_router, incorrect_router)

    await dp.start_polling(bot)


# Запуск основной функции
if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        pass
