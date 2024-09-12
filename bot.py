# Файл, содержащий объект бота


# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot


# Настройка работы файла
load_dotenv()


# Создание объекта бота
bot = Bot(token=getenv("BOT_TOKEN"))
