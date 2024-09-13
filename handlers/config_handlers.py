# Файл, содержащий обработчики команд бота для настройки групп


# Подключение модулей Python
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove


# Подключение пользовательских модулей
from handlers.middleware import Middleware
from handlers.states import (
    Create_Group,
    Add_Members,
    Delete_Group,
    Remove_Members,
    Assign_Reports_Recipient,
)
from handlers.markups import create_reply_markup, create_request_user_markup
from database.requests import User_Requests, Group_Requests


# Настройка работы файла
config_router = Router()
config_router.message.middleware(Middleware())


# Обработка команды "/creategroup"
@config_router.message(Command("creategroup"))
async def cmd_creategroup(message: Message, state: FSMContext) -> None:
    if len(await User_Requests.get_groups_where_creator(message.from_user.id)) == 25:
        mssg_txt = "Вы создали максимальное количество групп."

        await message.answer(mssg_txt)

        return

    await state.set_state(Create_Group.group_name)

    mssg_txt = "Введите название группы."

    await message.answer(mssg_txt)


# Получение названия группы от пользователя
@config_router.message(Create_Group.group_name)
async def get_group_name(message: Message, state: FSMContext) -> None:
    group_creator: int = message.from_user.id
    group_name: str = message.text.title()

    if len(group_name) > 25:
        mssg_txt = "Название группы слишком длинное, введите другое."

        await message.answer(mssg_txt)

        return
    elif not await Group_Requests.get_by_creator(group_creator, group_name) is None:
        mssg_txt = "Вы уже создавали группу с таким названием, введите другое."

        await message.answer(mssg_txt)

        return

    await Group_Requests.create(group_creator, group_name)

    await state.clear()

    mssg_txt = "Группа успешно создана."

    await message.answer(mssg_txt)


# Обработка команды "/addmembers"
@config_router.message(Command("addmembers"))
async def cmd_addmembers(message: Message, state: FSMContext) -> None:
    if await User_Requests.get_groups_where_creator(message.from_user.id) == []:
        mssg_txt = "Вы не создавали группу, в которую можно добавить участников."

        await message.answer(mssg_txt)

        return

    await state.set_state(Add_Members.group_name)

    mssg_txt = "Выберите группу из списка."
    markup: ReplyKeyboardMarkup = await create_reply_markup(
        await User_Requests.get_groups_where_creator(message.from_user.id)
    )

    await message.answer(mssg_txt, reply_markup=markup)


# Получение названия группы от пользователя
@config_router.message(Add_Members.group_name)
async def get_group_name(message: Message, state: FSMContext) -> None:
    group_creator: int = message.from_user.id
    group_name: str = message.text.title()
    group_members: list[str] = (
        await Group_Requests.get_by_creator(group_creator, group_name)
    ).members.split(";\n")

    if await Group_Requests.get_by_creator(group_creator, group_name) is None:
        mssg_txt = "Вы не создавали группу с таким названием, введите другое."

        await message.answer(mssg_txt)

        return
    elif len(group_members) == 25:
        await state.clear()

        mssg_txt = "Добавление участников в группу прервано, так как в выбранной группе содержится максимальное количество участников."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)

        return

    await state.update_data(group=group_name)
    await state.set_state(Add_Members.group_members)

    mssg_txt = "Введите имена участников."
    markup: ReplyKeyboardMarkup = await create_reply_markup([], True)

    await message.answer(mssg_txt, reply_markup=markup)


# Получение участника группы от пользователя
@config_router.message(Add_Members.group_members)
async def get_group_member(message: Message, state: FSMContext) -> None:
    group_creator: int = message.from_user.id
    group_name: str = (await state.get_data())["group"]
    group_members: list[str] = (
        await Group_Requests.get_by_creator(group_creator, group_name)
    ).members.split(";\n")
    group_member: str = message.text.title()

    if len(group_member) > 25:
        mssg_txt = "Участник не был добавлен, по причине превышения размера имени."

        await message.answer(mssg_txt)

        return
    elif group_member in group_members:
        mssg_txt = "Участник не был добавлен, по причине существования в группе."

        await message.answer(mssg_txt)

        return

    if group_member == "Стоп":
        await state.clear()

        mssg_txt = "Добавление участников в группу закончено."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)
    else:
        await Group_Requests.add_member(group_creator, group_name, group_member)

        mssg_txt = "Участник успешно добавлен в группу."

        await message.answer(mssg_txt)

        if len(group_members) == 24:
            await state.clear()

            mssg_txt = "Добавление участников в группу прервано, так как в выбранной группе содержится максимальное количество участников."

            await message.answer(mssg_txt)


# Обработка команды "/deletegroup"
@config_router.message(Command("deletegroup"))
async def cmd_deletegroup(message: Message, state: FSMContext):
    if await User_Requests.get_groups_where_creator(message.from_user.id) == []:
        mssg_txt = "Вы не создавали группу, которую можно удалить."

        await message.answer(mssg_txt)

        return

    await state.set_state(Delete_Group.group_name)

    mssg_txt = "Выберите группу из списка."
    markup: ReplyKeyboardMarkup = await create_reply_markup(
        await User_Requests.get_groups_where_creator(message.from_user.id)
    )

    await message.answer(mssg_txt, reply_markup=markup)


# Получение названия группы от пользователя
@config_router.message(Delete_Group.group_name)
async def get_group_name(message: Message, state: FSMContext):
    group_creator: int = message.from_user.id
    group_name: str = message.text.title()

    if await Group_Requests.get_by_creator(group_creator, group_name) is None:
        mssg_txt = "Вы не создавали группу с таким названием, введите другое."

        await message.answer(mssg_txt)

        return

    await state.update_data(group_name=group_name)

    await state.set_state(Delete_Group.confirmation)

    mssg_txt = "Вы уверены, что хотите удалить группу?\n"
    mssg_txt += 'Для подтверждения нажмите на кнопку с текстом "Удалить".\n'
    mssg_txt += 'Для отмены нажмите на кнопку с текстом "Отмена".'
    markup: ReplyKeyboardMarkup = await create_reply_markup(["Удалить", "Отмена"])

    await message.answer(mssg_txt, reply_markup=markup)


# Получение подтверждения от пользователя
@config_router.message(Delete_Group.confirmation)
async def get_confirmation(message: Message, state: FSMContext):
    confirmation: str = message.text.title()

    if confirmation != "Удалить" and confirmation != "Отмена":
        mssg_txt = "Неверный ответ, отправьте другой."

        await message.answer(mssg_txt)

        return

    if message.text.title() == "Удалить":
        group_creator: int = message.from_user.id
        group_name: str = (await state.get_data())["group_name"]

        await Group_Requests.delete(group_creator, group_name)

        await state.clear()

        mssg_txt = "Группа успешно удалена."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)
    else:
        await state.clear()

        mssg_txt = "Удаление группы отменено."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)


# Обработка команды "/removemembers"
@config_router.message(Command("removemembers"))
async def cmd_removemembers(message: Message, state: FSMContext) -> None:
    if await User_Requests.get_groups_where_creator(message.from_user.id) == []:
        mssg_txt = "Вы не создавали группу, из которой можно удалить участников."

        await message.answer(mssg_txt)

        return

    await state.set_state(Remove_Members.group_name)

    mssg_txt = "Выберите группу из списка."
    markup: ReplyKeyboardMarkup = await create_reply_markup(
        await User_Requests.get_groups_where_creator(message.from_user.id)
    )

    await message.answer(mssg_txt, reply_markup=markup)


# Получение названия группы от пользователя
@config_router.message(Remove_Members.group_name)
async def get_group_name(message: Message, state: FSMContext) -> None:
    group_creator: int = message.from_user.id
    group_name: str = message.text.title()
    group_members: list[str] = (
        await Group_Requests.get_by_creator(group_creator, group_name)
    ).members.split(";\n")

    if await Group_Requests.get_by_creator(group_creator, group_name) is None:
        mssg_txt = "Вы не создавали группу с таким названием, введите другое."

        await message.answer(mssg_txt)

        return
    elif group_members == [""]:
        await state.clear()

        mssg_txt = (
            "Удаление участников отменено, так как в группе отсутствуют участники."
        )
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)

        return

    await state.update_data(group_name=group_name)
    await state.set_state(Remove_Members.group_members)

    mssg_txt = "Выберите участников из списка."
    group_members.sort()
    markup: ReplyKeyboardMarkup = await create_reply_markup(group_members, True)

    await message.answer(mssg_txt, reply_markup=markup)


# Получение участника группы от пользователя
@config_router.message(Remove_Members.group_members)
async def get_group_member(message: Message, state: FSMContext):
    group_creator: int = message.from_user.id
    group_name: str = (await state.get_data())["group_name"]
    group_members: list[str] = (
        await Group_Requests.get_by_creator(group_creator, group_name)
    ).members.split(";\n")
    group_member: str = message.text.title()

    if group_member != "Стоп" and not group_member in group_members:
        mssg_txt = "Участник не был удален, по причине отсутствия в группе."
        markup: ReplyKeyboardMarkup = await create_reply_markup(group_members, True)

        await message.answer(mssg_txt, reply_markup=markup)

        return

    if group_member == "Стоп":
        await state.clear()

        mssg_txt = "Удаление участников из группы закончено."
        markup = ReplyKeyboardRemove()

        await message.answer(mssg_txt, reply_markup=markup)
    else:
        await Group_Requests.remove_member(group_creator, group_name, group_member)
        group_members.remove(group_member)

        if group_members == []:
            await state.clear()

            mssg_txt = "Удаление участников из группы закончено, так как в группе нет участников."
            markup = ReplyKeyboardRemove()

            await message.answer(mssg_txt, reply_markup=markup)

        else:
            mssg_txt = "Участник успешно удалён из группы."
            group_members.sort()
            markup: ReplyKeyboardMarkup = await create_reply_markup(group_members, True)

            await message.answer(mssg_txt, reply_markup=markup)


# Обработка команды "/assignreportsrecipient"
@config_router.message(Command("assignreportsrecipient"))
async def cmd_assignreportsrecipient(message: Message, state: FSMContext):
    if await User_Requests.get_groups_where_creator(message.from_user.id) == []:
        mssg_txt = (
            "Вы не создавали группу, для которой можно назначить получателя отчётов."
        )

        await message.answer(mssg_txt)

        return

    await state.set_state(Assign_Reports_Recipient.group_name)

    mssg_txt = "Выберите группу из списка."
    markup: ReplyKeyboardMarkup = await create_reply_markup(
        await User_Requests.get_groups_where_creator(message.from_user.id)
    )

    await message.answer(mssg_txt, reply_markup=markup)


# Получение названия группы от пользователя
@config_router.message(Assign_Reports_Recipient.group_name)
async def get_group_name(message: Message, state: FSMContext):
    group_creator: int = message.from_user.id
    group_name: str = message.text

    if await Group_Requests.get_by_creator(group_creator, group_name) is None:
        mssg_txt = "Вы не создавали группу с таким названием, введите другое."

        await message.answer(mssg_txt)

        return

    await state.update_data(group_name=group_name)
    await state.set_state(Assign_Reports_Recipient.group_reports_recipient)

    mssg_txt = "Нажмите на кнопку и выберите получателя отчётов."
    markup: ReplyKeyboardMarkup = await create_request_user_markup()

    await message.answer(mssg_txt, reply_markup=markup)


# Получение получателя отчётов
@config_router.message(Assign_Reports_Recipient.group_reports_recipient, F.users_shared)
async def get_group_reports_recipient(message: Message, state: FSMContext):
    group_creator: int = message.from_user.id
    group_name: str = (await state.get_data())["group_name"]
    group_reports_recipient: int = message.users_shared.user_ids[0]

    try:
        await Group_Requests.assign_reports_recipient(
            group_creator, group_name, group_reports_recipient
        )
    except AttributeError:
        mssg_txt = "Вы не можете выбирать пользователя, который не запускал бота."

        await message.answer(mssg_txt)

        return

    await state.clear()

    mssg_txt = "Получатель отчётов успешно назначен."
    markup = ReplyKeyboardRemove()

    await message.answer(mssg_txt, reply_markup=markup)
