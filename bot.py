# Файл, содержащий объект бота


# Подключение модулей Python
from aiogram import Bot


# Подключение пользовательских модулей
from config import BOT_TOKEN


# Создание объекта бота
bot = Bot(token=BOT_TOKEN)
