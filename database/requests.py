# Файл, содержащий запросы в базу данных


# Подключение модулей Python
from datetime import datetime, date as Date, timezone, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import select, update


# Подключение пользовательских модулей
from database.models import session, User, Group, Report


# Класс для работы с датой и временем
class Datetime_Handler:
    """Класс для работы с датой и временем"""

    # Статический метод для получения даты в часовом поясе по смещению UTC
    @staticmethod
    async def get_local_date(utc_offset: int) -> Date:
        date: Date = datetime.now(timezone(timedelta(seconds=utc_offset))).date()

        return date

    # Метод класса для получения даты начала текущей недели в часовом поясе по смещению UTC
    @classmethod
    async def get_start_of_week(cls, utc_offset: int) -> Date:
        date: Date = await cls.get_local_date(utc_offset)
        weekday: int = date.weekday()
        date -= relativedelta(days=weekday)

        return date

    # Метод класса для получения даты начала текущего месяца в часовом поясе по смещению UTC
    @classmethod
    async def get_start_of_month(cls, utc_offset: int) -> Date:
        date: Date = (await cls.get_local_date(utc_offset)).replace(day=1)

        return date

    # Метод класса для получения даты начала текущего года в часовом поясе по смещению UTC
    @classmethod
    async def get_start_of_year(cls, utc_offset: int) -> Date:
        date: Date = (await cls.get_local_date(utc_offset)).replace(month=1, day=1)

        return date

    @staticmethod
    async def validate_date(date: str) -> bool:
        parts = date.split(".")

        if len(parts) != 3:
            return False

        day, month, year = parts

        try:
            day = int(day)
            month = int(month)
            year = int(year)
        except ValueError:
            return False

        if not 1 <= day <= 31:
            return False
        if not 1 <= month <= 12:
            return False
        if not 2000 <= year < 3000:
            return False

        return True


# Класс для описания запросов о пользователе базу данных
class User_Requests:
    """Класс для описания запросов о пользователях в базу данных"""

    # Статический метод для получения объекта пользователя из базы данных по его Телеграм id
    @staticmethod
    async def get(tg_id: int) -> User | None:
        async with session() as sess:
            user: User | None = await sess.scalar(
                select(User).where(User.tg_id == tg_id)
            )

            return user

    # Статический метод для получения Телеграм id пользователя по его id в базе данных
    @staticmethod
    async def get_tg_id(id: int) -> int:
        async with session() as sess:
            user: User | None = await sess.scalar(select(User).where(User.id == id))

            return user.tg_id

    # Метод класса для получения списка групп, которые создал пользователь по его Телеграм id
    @classmethod
    async def get_groups_where_creator(cls, tg_id: int) -> list[str]:
        async with session() as sess:
            id: int = (await cls.get(tg_id)).id

            groups: list[str] = [
                group.name
                for group in await sess.scalars(
                    select(Group).where(Group.creator == id)
                )
            ]
            groups.sort()

            return groups

    # Метод класса для получения списка групп, в которых пользователь назначен получателем отчётов по его Телеграм id
    @classmethod
    async def get_groups_where_reports_recipient(cls, tg_id: int) -> list[str]:
        async with session() as sess:
            id: int = (await cls.get(tg_id)).id

            groups: list[str] = [
                group.name
                for group in await sess.scalars(
                    select(Group).where(Group.reports_recipient == id)
                )
            ]
            groups.sort()

            return groups

    # Метод класса для инициализации пользователя в базе данных по его Телеграм id
    @classmethod
    async def init(cls, tg_id: int) -> None:
        async with session() as sess:
            user: User | None = await cls.get(tg_id)

            if user is None:
                default_utc_offset = 10800

                sess.add(User(tg_id=tg_id, utc_offset=default_utc_offset))

                await sess.commit()

    # Статический метод для установки смещения UTC пользователя в базе данных по его Телеграм id
    @staticmethod
    async def set_utc_offset(tg_id: int, utc_offset: int) -> None:
        async with session() as sess:
            await sess.execute(
                update(User).where(User.tg_id == tg_id).values(utc_offset=utc_offset)
            )

            await sess.commit()


# Класс для описания запросов о группах в базу данных
class Group_Requests:
    """Класс для описания запросов о группах в базу данных"""

    # Статический метод для получения объекта группы из базы данных по Телеграм id создателя и её имени
    @staticmethod
    async def get_by_creator(creator_tg_id: int, name: str) -> Group | None:
        async with session() as sess:
            creator: int = (await User_Requests.get(creator_tg_id)).id
            group: Group | None = await sess.scalar(
                select(Group).where(Group.creator == creator).where(Group.name == name)
            )

            return group

    # Статический метод для получения объекта группы из базы данных по Телеграм id получателя отчётов и её имени
    @staticmethod
    async def get_by_reports_recipient(
        name: str, reports_recipient_tg_id: int
    ) -> Group | None:
        async with session() as sess:
            reports_recipient: int = (
                await User_Requests.get(reports_recipient_tg_id)
            ).id
            group: Group | None = await sess.scalar(
                select(Group)
                .where(Group.name == name)
                .where(Group.reports_recipient == reports_recipient)
            )

            return group

    # Метод класса для получения статистики о отсутствии участников группы по её имени, Телеграм id получателя отчётов и
    # датам начала и конца периода времени, для которого она получается
    @classmethod
    async def get_statistics(
        cls,
        name: str,
        reports_recipient_tg_id: int,
        date_from: str,
        date_to: str = None,
    ) -> str:
        async with session() as sess:
            id = (await cls.get_by_reports_recipient(name, reports_recipient_tg_id)).id
            reports_recipient_utc_offset: int = (
                await User_Requests.get(reports_recipient_tg_id)
            ).utc_offset

            if date_from == "Неделя":
                date_from: Date = await Datetime_Handler.get_start_of_week(
                    reports_recipient_utc_offset
                )
                date_to: Date = await Datetime_Handler.get_local_date(
                    reports_recipient_utc_offset
                )
            elif date_from == "Месяц":
                date_from: Date = await Datetime_Handler.get_start_of_month(
                    reports_recipient_utc_offset
                )
                date_to: Date = await Datetime_Handler.get_local_date(
                    reports_recipient_utc_offset
                )
            elif date_from == "Год":
                date_from: Date = await Datetime_Handler.get_start_of_year(
                    reports_recipient_utc_offset
                )
                date_to: Date = await Datetime_Handler.get_local_date(
                    reports_recipient_utc_offset
                )
            else:
                date_from: Date = datetime.strptime(date_from, "%d.%m.%Y")
                date_to: Date = datetime.strptime(date_to, "%d.%m.%Y")

            reports = await sess.scalars(
                select(Report)
                .where(Report.group == id)
                .where(Report.date >= date_from)
                .where(Report.date <= date_to)
            )
            cnt_reports: int = 0
            reports_with_member: dict[str, int] = {}

            for report in reports:
                cnt_reports += 1
                report_members: list[str] = report.members.split(";\n")

                for member in report_members:
                    if not member in reports_with_member:
                        reports_with_member[member] = 0

                    reports_with_member[member] += 1

            reports_with_member_sorted: list = sorted(
                reports_with_member.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            cnt_reports_members: int = len(reports_with_member)

            if cnt_reports_members == 0:
                statistics = f'С {date_from.strftime("%d.%m.%Y")} по {date_to.strftime("%d.%m.%Y")} в группе "{name}" отсутствующих не было.'

                return statistics
            else:
                statistics = f'Статистика отсутствия участников группы "{name}" с {date_from.strftime("%d.%m.%Y")} по {date_to.strftime("%d.%m.%Y")}:\n'

                for i in range(cnt_reports_members):
                    member: str = reports_with_member_sorted[i][0]
                    reports_with_this_member: int = reports_with_member_sorted[i][1]
                    reports_with_this_member_percentages = int(
                        reports_with_this_member / cnt_reports * 100
                    )

                    statistics += f"{i + 1}. {member} - Присутствовал в {reports_with_this_member} отчётах из {cnt_reports} "
                    statistics += f"({reports_with_this_member_percentages}%)"

                    if i < cnt_reports_members - 1:
                        statistics += ";\n"
                    else:
                        statistics += "."

                    return statistics

    # Статический метод для создания (записи) группы в базе данных по Телеграм id создателя и её имени
    @staticmethod
    async def create(creator_tg_id: int, name: str) -> None:
        async with session() as sess:
            creator: int = (await User_Requests.get(creator_tg_id)).id

            sess.add(
                Group(creator=creator, name=name, reports_recipient=creator, members="")
            )

            await sess.commit()

    # Метод класса для добавления (записи) участника группы в группу в базе данных по Телеграм id создателя группы, её имени и имени участника
    @classmethod
    async def add_member(cls, creator_tg_id: int, name: str, member: str) -> None:
        async with session() as sess:
            creator: int = (await User_Requests.get(creator_tg_id)).id
            members: list[str] = (await cls.get_by_creator(creator_tg_id, name)).members

            if members == "":
                members: list[str] = []
            else:
                members: list[str] = members.split(";\n")

            members.append(member)
            members: str = ";\n".join(members)

            await sess.execute(
                update(Group)
                .where(Group.creator == creator)
                .where(Group.name == name)
                .values(members=members)
            )

            await sess.commit()

    # Метод класса для удаления группы из базы данных по Телеграм id создателя и её имени
    @classmethod
    async def delete(cls, creator_tg_id: int, name: str) -> None:
        async with session() as sess:
            group: Group | None = await cls.get_by_creator(creator_tg_id, name)

            await sess.delete(group)

            await sess.commit()

    # Метод класса для удаления участника из группы в базе данных по Телеграм id создателя группы, её имени и имени участника
    @classmethod
    async def remove_member(cls, creator_tg_id: int, name: str, member: str) -> None:
        async with session() as sess:
            creator: int = (await User_Requests.get(creator_tg_id)).id
            members: list[str] = (
                await cls.get_by_creator(creator_tg_id, name)
            ).members.split(";\n")
            members.remove(member)
            members: str = ";\n".join(members)

            await sess.execute(
                update(Group)
                .where(Group.creator == creator)
                .where(Group.name == name)
                .values(members=members)
            )

            await sess.commit()

    # Статический метод для назначения получателя отчётов группы в базе данных по Телеграм id создателя, её имени и id получателя
    @staticmethod
    async def assign_reports_recipient(
        creator_tg_id: int, name: str, reports_recipient_tg_id: int
    ) -> None:
        async with session() as sess:
            creator: int = (await User_Requests.get(creator_tg_id)).id
            reports_recipient: int = (
                await User_Requests.get(reports_recipient_tg_id)
            ).id

            await sess.execute(
                update(Group)
                .where(Group.creator == creator)
                .where(Group.name == name)
                .values(reports_recipient=reports_recipient)
            )

            await sess.commit()


# Класс для описания запросов об отчётах группы в базу данных
class Report_Requests:
    """Класс для описания запросов об отчётах группы в базу данных"""

    # Статический метод для получения объекта сегодняшнего отчёта из базы данных по Телеграм id создателя группы и её имени
    async def get(group_creator_tg_id: int, group_name: str) -> Report:
        async with session() as sess:
            user: User | None = await User_Requests.get(group_creator_tg_id)
            group: int = (
                await Group_Requests.get_by_creator(group_creator_tg_id, group_name)
            ).id
            date: Date = await Datetime_Handler.get_local_date(user.utc_offset)
            report: Report | None = await sess.scalar(
                select(Report).where(Report.group == group).where(Report.date == date)
            )

            return report

    # Статический метод для получения файла отчётов из базы данных по Telegram id создателя группы, её имени и датам начала и конца промежутка времени,
    # для которого получается файл
    @staticmethod
    async def get_file(
        group_name: str,
        group_reports_recipient_tg_id: int,
        date_from: str,
        date_to: str = None,
    ):
        async with session() as sess:
            group = await Group_Requests.get_by_reports_recipient(
                group_name, group_reports_recipient_tg_id
            )
            group_id: int = group.id
            # Получение имени создателя группы
            # Получение имени создателя группы
            # Получение имени создателя группы
            group_reports_recipient_utc_offset: int = (
                await User_Requests.get(group_reports_recipient_tg_id)
            ).utc_offset

            if date_from == "Неделя":
                date_from: Date = await Datetime_Handler.get_start_of_week(
                    group_reports_recipient_utc_offset
                )
                date_to: Date = await Datetime_Handler.get_local_date(
                    group_reports_recipient_utc_offset
                )
            elif date_from == "Месяц":
                date_from: Date = await Datetime_Handler.get_start_of_month(
                    group_reports_recipient_utc_offset
                )
                date_to: Date = await Datetime_Handler.get_local_date(
                    group_reports_recipient_utc_offset
                )
            elif date_from == "Год":
                date_from: Date = await Datetime_Handler.get_start_of_year(
                    group_reports_recipient_utc_offset
                )
                date_to: Date = await Datetime_Handler.get_local_date(
                    group_reports_recipient_utc_offset
                )
            else:
                date_from: Date = datetime.strptime(date_from, "%d.%m.%Y")
                date_to: Date = datetime.strptime(date_to, "%d.%m.%Y")

            reports: list[Report] = await sess.scalars(
                select(Report)
                .where(Report.group == group_id)
                .where(Report.date >= date_from)
                .where(Report.date <= date_to)
            )

            for report in reports:
                data: list = [report.date, group_name, report.members]
                # Создание файла reports.xlsx
                # Создание файла reports.xlsx
                # Создание файла reports.xlsx

    # Статический метод для создания сегодняшнего отчёта в базе данных по Телеграм id создателя группы, её имени и списку участников отчёта
    async def create(
        group_creator_tg_id: int, group_name: str, members: list[str]
    ) -> None:
        async with session() as sess:
            user: User | None = await User_Requests.get(group_creator_tg_id)
            group: int = (
                await Group_Requests.get_by_creator(group_creator_tg_id, group_name)
            ).id
            date: Date = await Datetime_Handler.get_local_date(user.utc_offset)
            members: str = ";\n".join(members)

            sess.add(
                Report(
                    group=group,
                    date=date,
                    members=members,
                )
            )

            await sess.commit()

    # Статический метод для редактирования отчёта в базе данных по Телеграм id создателя группы, её имени, дате создания отчёта и списку участников отчёта
    async def edit(
        group_creator_tg_id: int, group_name: str, members: list[str]
    ) -> None:
        async with session() as sess:
            user: User | None = await User_Requests.get(group_creator_tg_id)
            group: int = (
                await Group_Requests.get_by_creator(group_creator_tg_id, group_name)
            ).id
            date: Date = await Datetime_Handler.get_local_date(user.utc_offset)
            members: str = ";\n".join(members)

            await sess.execute(
                update(Report)
                .where(Report.group == group)
                .where(Report.date == date)
                .values(members=members)
            )

            await sess.commit()
