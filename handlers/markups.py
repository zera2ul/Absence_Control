# Файл, содержащий функции для создания клавиатур бота


# Подключение модулей Python
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButtonRequestUsers,
)
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    InlineKeyboardBuilder,
)


# Функция, создающая reply разметку, используя список текста на кнопках и добавляя кнопку с текстом "Стоп" при необходимости
async def create_reply_markup(
    data: list[str], add_stop_button: bool = False
) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    for element in data:
        keyboard.add(KeyboardButton(text=element))
    keyboard.adjust(2)

    if add_stop_button:
        keyboard.row(KeyboardButton(text="Стоп"))

    markup: ReplyKeyboardMarkup = keyboard.as_markup()

    return markup


# Функция, создающая reply разметку, которая содержит кнопку для запроса пользователя
async def create_request_user_markup() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Выбрать получателя отчётов.",
                    request_users=KeyboardButtonRequestUsers(
                        request_id=0, max_quantity=1
                    ),
                )
            ]
        ]
    )

    return markup


# Функция, создающая inline разметку для создания отчёта, используя список участников группы
async def create_report_markup(data: list[str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for element in data:
        keyboard.add(InlineKeyboardButton(text=element, callback_data=f"r_{element}"))
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="Отправить", callback_data="r_Отправить"))
    markup: InlineKeyboardMarkup = keyboard.as_markup()

    return markup
