# Файл, содержащий объект бота


# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot


# Настройка работы файла
load_dotenv()


# Создание объекта бота
bot = Bot(token=getenv("BOT_TOKEN"), session=AiohttpSession(proxy=getenv("PROXY_URL")))
