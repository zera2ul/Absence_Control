# Файл, содержащий middleware


# Подключение модулей Python
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


# Класс для описания внутреннего middleware
class Middleware(BaseMiddleware):
    """Класс для описания внутреннего middleware"""

    # Магический метод __call__, срабатывающий при вызове объекта класса
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.content_type == "text" or event.content_type == "users_shared":
            return await handler(event, data)
        else:
            mssg_txt = "Ваше сообщение не является текстом, отправьте другое."

            await event.answer(mssg_txt)
