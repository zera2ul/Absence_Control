# Файл, содержащий обработчик некорректных сообщений для бота


# Подключение модулей Python
from aiogram import Router
from aiogram.types import Message


# Настройка работы файла
incorrect_router = Router()


# Обработка некорректных сообщений
@incorrect_router.message()
async def handle_incorrect_message(message: Message):
    mssg_txt = "Ваше сообщение не является корректной командой."

    await message.answer(mssg_txt)
