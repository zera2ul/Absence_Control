# Файл, содержащий объект бота


# Подключение модулей Python
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot


# Подключение пользовательских модулей
from config import BOT_TOKEN, PROXY_URL


# Создание объекта бота
bot = Bot(token=BOT_TOKEN, session=AiohttpSession(proxy=PROXY_URL))
