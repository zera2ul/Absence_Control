# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv
from requests import post
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext


# Подключение пользовательских модулей
from handlers.middleware import Middleware
from handlers.states import Create_Report, Create_Statistics
from handlers.markups import create_reply_markup, create_report_markup
from database.requests import User_Requests, Group_Requests, Report_Requests


# Настройка работы файла
load_dotenv()

work_router = Router()
work_router.message.middleware(Middleware())


# Обработка команды "/createreport"
@work_router.message(Command("createreport"))
async def cmd_createreport(message: Message, state: FSMContext) -> None:
    groups: list = await User_Requests.get_groups_where_creator(message.from_user.id)

    if groups == []:
        mssg_txt = "Вы не создавали группу, для которой можно создать отчёт."

        await message.answer(mssg_txt)

        return

    await state.set_state(Create_Report.group_name)

    mssg_txt = "Выберите группу из списка."
    markup: ReplyKeyboardMarkup = await create_reply_markup(groups)

    await message.answer(mssg_txt, reply_markup=markup)


# Получение названия группы от пользователя
@work_router.message(Create_Report.group_name)
async def get_group_name(message: Message, state: FSMContext) -> None:
    group_creator: int = message.from_user.id
    group_name: str = message.text
    group_members: list[str] = (
        await Group_Requests.get_by_creator(group_creator, group_name)
    ).members.split(";\n")

    if await Group_Requests.get_by_creator(group_creator, group_name) is None:
        mssg_txt = "Вы не создавали группу с таким названием, введите другое."

        await message.answer(mssg_txt)

        return
    elif group_members == []:
        await state.clear()

        mssg_txt = "Создание отчёта отменено, так как в группе отсутствуют участники."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)

        return

    await state.update_data(group_name=group_name, group_members=[])
    await state.set_state(Create_Report.group_members)

    mssg_txt = f'Создание отчёта для группы "{group_name}".'
    markup = ReplyKeyboardRemove()

    await message.answer(mssg_txt, reply_markup=markup)

    mssg_txt = "Для добавления участника в отчёт, нажмите кнопку с его именем.\n"
    mssg_txt += 'Для отправки отчёта нажмите кнопку "Отправить".'
    group_members.sort()
    markup: InlineKeyboardMarkup = await create_report_markup(group_members)

    await message.answer(mssg_txt, reply_markup=markup)


# Выбор участников для отчёта пользователем
@work_router.callback_query(Create_Report.group_members)
async def get_group_members(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.data == "r_Отправить":
        data = await state.get_data()
        group_creator: int = callback.from_user.id
        group_name: str = data["group_name"]
        group_reports_recipient: int = await User_Requests.get_tg_id(
            (
                await Group_Requests.get_by_creator(group_creator, group_name)
            ).reports_recipient
        )
        group_members: list[str] = data["group_members"]

        if await Report_Requests.get(group_creator, group_name) is None:
            await Report_Requests.create(group_creator, group_name, group_members)
        else:
            await Report_Requests.edit(group_creator, group_name, group_members)

            mssg_txt = f'Изменения в сегодняшнем отчёте для группы "{group_name}."'

            if not await send_message(group_reports_recipient, mssg_txt):
                mssg_txt = "Невозможно отправить сообщение получателю."

                await callback.answer(mssg_txt)

                return

        if len(group_members) == 0:
            mssg_txt = f'Сегодня в группе "{group_name}" отсутствующих нет.'

            if not await send_message(group_reports_recipient, mssg_txt):
                mssg_txt = "Невозможно отправить отчёт получателю."

                await callback.answer(mssg_txt)

                return
        else:
            mssg_txt = f'Сегодня в группе "{group_name}" отсутствуют:\n'
            group_members.sort()
            mssg_txt += ";\n".join(group_members)
            mssg_txt += "."

            if not await send_message(group_reports_recipient, mssg_txt):
                mssg_txt = "Невозможно отправить отчёт получателю."

                await callback.answer(mssg_txt)

                return

        mssg_txt = "Отчёт успешно отправлен."

        await callback.answer(mssg_txt)

        await state.clear()
    else:
        group_member: str = callback.data.split("_")[1].title()
        group_members: list[str] = (await state.get_data())["group_members"]

        if not group_member in group_members:
            group_members.append(group_member)

            mssg_txt = f'Участник "{group_member}" добавлен в отчёт.'

            await callback.answer(mssg_txt)
        else:
            mssg_txt = f'Участник "{group_member}" уже добавлен в отчёт.'

            await callback.answer(mssg_txt)


# Процедура для отправки сообщения пользователю
async def send_message(chat_id: int, text: str) -> bool:
    url = f'https://api.telegram.org/bot{getenv("BOT_TOKEN")}/sendMessage'
    json_info = {"chat_id": chat_id, "text": text}

    response = post(url, json=json_info)

    if response.status_code == 200:
        return True

    return False


# Обработка команды "/getstatistics"
@work_router.message(Command("getstatistics"))
async def cmd_getstatistics(message: Message, state: FSMContext) -> None:
    groups: list[str] = await User_Requests.get_groups_where_reports_recipient(
        message.from_user.id
    )
    if groups == []:
        mssg_txt = "Вы не назначены получателем отчётов ни в одной группе."

        await message.answer(mssg_txt)

        return

    await state.set_state(Create_Statistics.group_name)

    mssg_txt = "Выберите группу из списка."
    markup: ReplyKeyboardMarkup = await create_reply_markup(groups)

    await message.answer(mssg_txt, reply_markup=markup)


# Получение названия группы от пользователя
@work_router.message(Create_Statistics.group_name)
async def get_group_name(message: Message, state: FSMContext) -> None:
    group_name: str = message.text.title()
    reports_recipient: int = message.from_user.id

    if not group_name in await User_Requests.get_groups_where_reports_recipient(
        reports_recipient
    ):
        mssg_txt = "Вы не назначены получателем отчётов в группе с таким названием, выберите другую."

        await message.answer(mssg_txt)

        return

    await state.update_data(group_name=group_name)
    await state.set_state(Create_Statistics.period)

    mssg_txt = "Выберите период времени."
    markup: ReplyKeyboardMarkup = await create_reply_markup(["Неделя", "Месяц", "Год"])

    await message.answer(mssg_txt, reply_markup=markup)


# Получение периода времени от пользователя
@work_router.message(Create_Statistics.period)
async def get_time_period(message: Message, state: FSMContext) -> None:
    group_name: str = (await state.get_data())["group_name"]
    reports_recipient: int = message.from_user.id
    time_period = message.text.title()

    if not time_period in ["Неделя", "Месяц", "Год"]:
        mssg_txt = "Неверный промежуток времени, выберите другой."

        await message.answer(mssg_txt)

        return

    await state.clear()

    mssg_txt: str = await Group_Requests.get_statistics(
        group_name, reports_recipient, time_period
    )
    markup = ReplyKeyboardRemove()

    await message.answer(mssg_txt, reply_markup=markup)
