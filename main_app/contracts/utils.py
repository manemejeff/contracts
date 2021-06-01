import datetime
import calendar
from dateutil.rrule import rrule, MONTHLY, WEEKLY, SU


# looks like DRY violation -_-

def get_months_end(date1_str: str, date2_str: str) -> list:
    """
    Функция возвращает список дат являющихся окончаниями месяцев
    входящих в диапазон обозначенный входными параметрами.
    Если хоть одна дата в диапазоне принадлежит месяцу
    то месяц считается входящим в диапазон

    :param date1_str:
    :param date2_str:
    :return:
    """
    date1 = datetime.datetime.strptime(date1_str, '%Y-%m-%d')
    date2 = datetime.datetime.strptime(date2_str, '%Y-%m-%d')
    # print(date1)
    # print(date1.day)
    # print(calendar.monthrange(date1.year, date1.month))
    dates = [dt + datetime.timedelta(days=calendar.monthrange(dt.year, dt.month)[1] - dt.day) for dt in
             rrule(MONTHLY, dtstart=date1, until=date2)]
    # print(dates)
    return dates


def get_weeks_end(date1_str: str, date2_str: str) -> list:
    """
    Функция возвращает список дат являющихся окончанием недель
    входящих в диапазон дат, обозначенный входными параметрами

    :param date1_str:
    :param date2_str:
    :return:
    """
    date1 = datetime.datetime.strptime(date1_str, '%Y-%m-%d')
    date2 = datetime.datetime.strptime(date2_str, '%Y-%m-%d')
    dates = [dt for dt in
             rrule(WEEKLY, dtstart=date1, until=date2, byweekday=SU)]
    return dates


def date_range(start_date: str, end_date: str) -> datetime.datetime:
    """
    Генератор дат из диапазона

    :param start_date:
    :param end_date:
    :return:
    """

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


if __name__ == '__main__':
    # get_months_end('2021-03-2', '2021-05-25')
    get_weeks_end('2021-03-2', '2021-05-25')
