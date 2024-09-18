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
        if event.content_type == "text":
            if await data["state"].get_state() is None:
                await handler(event, data)
            else:
                commands = [
                    "/start",
                    "/help",
                    "/setutcoffset",
                    "/feedback",
                    "/creategroup",
                    "/addmembers",
                    "/deletegroup",
                    "/removemembers",
                    "/assignreportsrecipient",
                    "/createreport",
                    "/getstatistics",
                    "/getreportsfile",
                ]

                if not event.text in commands:
                    return await handler(event, data)
                else:
                    mssg_txt = "Вы не можете воспользоваться данной командой во время выполнения другой."

                    await event.answer(mssg_txt)
        elif event.content_type == "users_shared":
            await handler(event, data)
        else:
            mssg_txt = "Ваше сообщение не является текстом, отправьте другое."

            await event.answer(mssg_txt)
