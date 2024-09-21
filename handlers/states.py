# Файл, содержащий состояния


# Подключение модулей Python
from aiogram.fsm.state import StatesGroup, State


# Класс для описания состояния пользователя, когда он устанавливает смещение UTC
class Set_Utc_Offset(StatesGroup):
    """Класс для описания состояния пользователя, когда он устанавливает смещение UTC"""

    utc_offset = State()


# Класс для описания состояния пользователя, когда он отправляет отзыв
class Send_Feedback(StatesGroup):
    """Класс для описания состояния пользователя, когда он отправляет отзыв"""

    feedback = State()
    answer = State()


# Класс для описания состояния пользователя, когда он создаёт группу
class Create_Group(StatesGroup):
    """Класс для описания состояния пользователя, когда он создаёт группу"""

    group_name = State()


# Класс для описания состояния пользователя, когда он добавляет участников в группу
class Add_Members(StatesGroup):
    """Класс для описания состояния пользователя, когда он добавляет участников в группу"""

    group_name = State()
    group_members = State()


# Клас для описания состояния пользователя, когда он удаляет группу
class Delete_Group(StatesGroup):
    """Клас для описания состояния пользователя, когда он удаляет группу"""

    group_name = State()
    confirmation = State()


# Класс для описания состояния пользователя, когда он удаляет участников из группы
class Remove_Members(StatesGroup):
    """Класс для описания состояния пользователя, когда он удаляет участников из группы"""

    group_name = State()
    group_members = State()


# Класс для описания состояния пользователя, когда он назначает получателя отчётов для группы
class Assign_Reports_Recipient(StatesGroup):
    """Класс для описания состояния пользователя, когда он назначает получателя отчётов для группы"""

    group_name = State()
    group_reports_recipient = State()


# Класс для описания состояния пользователя, когда он создаёт отчёт об отсутствии участников группы
class Create_Report(StatesGroup):
    """Класс для описания состояния пользователя, когда он создаёт отчёт об отсутствии участников группы"""

    group_name = State()
    group_members = State()


# Класс для описания состояния пользователя, когда он получает статистику об отсутствии участников группы
class Get_Statistics(StatesGroup):
    """Класс для описания состояния пользователя, когда он получает статистику об отсутствии участников группы"""

    group_name = State()
    date_from = State()
    date_to = State()


# Класс для описания состояния пользователя, когда он получает файл с отчётами об отсутствии участников групп
class Get_Reports_File(StatesGroup):
    """Класс для описания состояния пользователя, когда он получает файл с отчётами об отсутствии участников групп"""

    group_name = State()
    date_from = State()
    date_to = State()
    file_format = State()
