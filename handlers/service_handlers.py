# Файл, содержащий обработчики служебных команд бота


# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext


# Подключение пользовательских модулей
from bot import bot
from handlers.middleware import Middleware
from handlers.states import Set_Utc_Offset, Send_Feedback
from database.requests import User_Requests


# Настройка работы файла
load_dotenv()

service_router = Router()
service_router.message.middleware(Middleware())


# Обработка команды "/start"
@service_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await User_Requests.init(message.from_user.id)

    mssg_txt = f"Здравствуйте, {message.from_user.full_name}!\n"
    mssg_txt += (
        "Этот бот предназначен для создания отчётов об отсутствии участников групп.\n"
    )
    mssg_txt += 'Для получения более подробной справочной информации воспользуйтесь командой "/help".'

    await message.answer(mssg_txt)


# Обработка команды "/help"
@service_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    mssg_txt1 = "При помощи данного бота вы можете создать группу.\n"
    mssg_txt1 += "Также у вас есть возможность добавить в группу участников.\n"
    mssg_txt1 += "Количество групп и участников не может превышать 25.\n"
    mssg_txt1 += "Имена групп, как и имена участников, не должны превышать длину в 25 символов.\n"
    mssg_txt1 += "При добавлении и удалении участников каждое имя отправляется в новом сообщении. "
    mssg_txt1 += 'Для окончания отправки имён нажмите на кнопку с текстом "Стоп".\n'
    mssg_txt1 += "После создания группы вы являетесь её получателем отчётов, "
    mssg_txt1 += "однако вы можете назначить на эту роль другого пользователя, который хотя бы раз запускал бота, используя специальную команду.\n"
    mssg_txt1 += "Но один и тот же пользователь не может быть получателем отчётов для 2 групп с одинаковыми названиями.\n"
    mssg_txt1 += (
        "После настройки группы вы сможете создать отчёт и отправить его получателю. "
    )
    mssg_txt1 += "Если вы будете отправлять отчёт для одной и той же группы больше одного раза в день, то получателю будет сообщаться, что отчёт изменился.\n"
    mssg_txt1 += "Также данный бот при создании отчётов будет сохранять дату их создания для подведения статистики за определённый промежуток времени.\n"
    mssg_txt1 += "В данном боте присутствует возможность отправить отзыв владельцу, который может связаться с вами в случае необходимости.\n"

    mssg_txt1 += "По умолчанию бот будет работать в часовом поясе UTC +10800 секунд (UTC +3:00). "
    mssg_txt1 += "Если вы живёте в другом часовом поясе, то рекомендуется указать его боту при помощи специальной команды. "
    mssg_txt1 += 'Время указывается в секундах, со знаком "-" (без кавычек), если смещение отрицательное, иначе без знака.\n\n'

    mssg_txt2 = (
        "Для взаимодействия с ботом вы можете воспользоваться следующими командами:\n"
    )
    mssg_txt2 += "/start - Начать диалог с ботом;\n"
    mssg_txt2 += "/help - Получить справочную информацию;\n"
    mssg_txt2 += "/cancel - Отменить выполнение текущей команды;\n"
    mssg_txt2 += "/setutcoffset - Указать смещение UTC в вашем часовом поясе;\n"
    mssg_txt2 += "/feedback - Отправить отзыв о боте его владельцу;\n"
    mssg_txt2 += "/creategroup - Создать группу;\n"
    mssg_txt2 += "/addmembers - Добавить участников в группу;\n"
    mssg_txt2 += "/deletegroup - Удалить группу;\n"
    mssg_txt2 += "/removemembers - Удалить участников из группы;\n"
    mssg_txt2 += "/assignreportsrecipient - Назначить получателя отчётов для группы;\n"
    mssg_txt2 += (
        "/createreport - Создать и отправить отчёт об отсутствии участников группы;\n"
    )
    mssg_txt2 += "/getstatistics - Получить статистику об отсутствии участников группы.\n"
    mssg_txt2 += "/getreportsfile - Получить файл отчётов об отсутствии участников групп"

    mssg_txt: str = mssg_txt1 + mssg_txt2

    await message.answer(mssg_txt)


# Обработка команды "/cancel"
@service_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if not await state.get_state() is None:
        await state.clear()

        mssg_txt = "Команда отменена."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)
    else:
        mssg_txt = 'Команда "/cancel" не сработала из-за отсутствия выполняемых команд.'

        await message.answer(mssg_txt)


# Обработка команды "/setutcoffset"
@service_router.message(Command("setutcoffset"))
async def cmd_setutcoffset(message: Message, state: FSMContext) -> None:
    await state.set_state(Set_Utc_Offset.utc_offset)

    mssg_txt = "Введите смещение UTC."

    await message.answer(mssg_txt)


# Получение смещения UTC от пользователя
@service_router.message(Set_Utc_Offset.utc_offset)
async def get_utc_offset(message: Message, state: FSMContext) -> None:
    utc_offset: str = message.text

    try:
        utc_offset: int = int(utc_offset)
    except ValueError:
        mssg_txt = "Смещение UTC должно быть целым числом, введите другое."

        await message.answer(mssg_txt)

        return

    min_time = -86400
    max_time = 86400

    if not min_time < utc_offset < max_time:
        mssg_txt = (
            "Смещение UTC выходит за границы допустимых значений, введите другое."
        )

        await message.answer(mssg_txt)

        return

    await User_Requests.set_utc_offset(message.from_user.id, utc_offset)

    await state.clear()

    mssg_txt = "Смещение UTC успешно установлено."

    await message.answer(mssg_txt)


# Обработка команды "/feedback"
@service_router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext) -> None:
    feedbacks_cnt: int = (await User_Requests.get(message.from_user.id)).feedbacks_cnt

    if feedbacks_cnt == 5:
        mssg_txt = "Вы уже отправили максимальное количество отзывов за день."

        await message.answer(mssg_txt)

        return

    await state.set_state(Send_Feedback.feedback)

    mssg_txt = "Отправьте отзыв."

    await message.answer(mssg_txt)


# Получение отзыва от пользователя
@service_router.message(Send_Feedback.feedback)
async def get_feedback(message: Message, state: FSMContext) -> None:
    await state.clear()

    await User_Requests.increase_feedbacks_cnt(message.from_user.id)

    chat_id: int = int(getenv("OWNER_TG_ID"))
    user_name: str = message.from_user.username
    mssg_txt: str = f"Отзыв от пользователя @{user_name}.\n\n"
    mssg_txt += message.text

    await bot.send_message(chat_id, mssg_txt)

    mssg_txt = "Отзыв успешно отправлен."
    await message.answer(mssg_txt)
