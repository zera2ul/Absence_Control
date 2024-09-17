# Основной файл бота


# Подключение модулей Python
from asyncio import run
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Dispatcher


# Подключение пользовательских модулей
from bot import bot
from handlers.service_handlers import service_router
from handlers.config_handlers import config_router
from handlers.work_handlers import work_router
from handlers.incorrect_messages_handler import incorrect_router
from database.models import create_models
from database.requests import User_Requests


# Основная функция для начала работы бота
async def main() -> None:
    await create_models()

    dp = Dispatcher()
    dp.include_routers(service_router, config_router, work_router, incorrect_router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(User_Requests.reset_feedbacks_cnt, CronTrigger(hour=4, minute=0))
    scheduler.start()

    await dp.start_polling(bot)


# Запуск основной функции
if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        pass
