# Файл, содержащий состояния


# Подключение модулей Python
from aiogram.fsm.state import StatesGroup, State


# Класс для описания состояния бота, когда он устанавливает смещение UTC
class Set_Utc_Offset(StatesGroup):
    """Класс для описания состояния бота, когда он устанавливает смещение UTC"""

    utc_offset = State()


# Класс для описания состояния бота, когда он создаёт группу
class Create_Group(StatesGroup):
    """Класс для описания состояния бота, когда он создаёт группу"""

    group_name = State()


# Класс для описания состояния бота, когда он добавляет участников в группу
class Add_Members(StatesGroup):
    """Класс для описания состояния бота, когда он добавляет участников в группу"""

    group_name = State()
    group_members = State()


# Клас для описания состояния бота, когда он удаляет группу
class Delete_Group(StatesGroup):
    """Клас для описания состояния бота, когда он удаляет группу"""

    group_name = State()
    confirmation = State()


# Класс для описания состояния бота, когда он удаляет участников из группы
class Remove_Members(StatesGroup):
    """Класс для описания состояния бота, когда он удаляет участников из группы"""

    group_name = State()
    group_members = State()


# Класс для описания состояния бота, когда он назначает получателя отчётов для группы
class Assign_Reports_Recipient(StatesGroup):
    """Класс для описания состояния бота, когда он назначает получателя отчётов для группы"""

    group_name = State()
    group_reports_recipient = State()


# Класс для описания состояния бота, когда он создаёт отчёт об отсутствии участников группы
class Create_Report(StatesGroup):
    """Класс для описания состояния бота, когда он создаёт отчёт об отсутствии участников группы"""

    group_name = State()
    group_members = State()


# Класс для описания состояния бота, когда он создаёт статистику об отсутствии участников группы
class Create_Statistics(StatesGroup):
    """Класс для описания состояния бота, когда он создаёт статистику об отсутствии участников группы"""

    group_name = State()
    date_from = State()
    date_to = State()


# Класс для описания состояния бота, когда он создаёт файл с отчётами об отсутствии участников групп
class Create_Reports_File(StatesGroup):
    """Класс для описания состояния бота, когда он создаёт файл с отчётами об отсутствии участников групп"""

    group_name = State()
    date_from = State()
    date_to = State()

# Класс для описания состояния бота, когда он отправляет владельцу сообщение обратной связи
class Send_Feedback(StatesGroup):
    """Класс для описания состояния бота, когда он отправляет владельцу сообщение обратной связи"""

    feedback = State()