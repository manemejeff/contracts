import datetime
from dateutil.rrule import rrule, MONTHLY, WEEKLY, SU
import calendar
from typing import List

from django.db.models import QuerySet, Sum
import pandas as pd

from .models import Contract, ContractType, Currency, Organization


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
    dates = [dt + datetime.timedelta(days=calendar.monthrange(dt.year, dt.month)[1] - dt.day) for dt in
             rrule(MONTHLY, dtstart=date1, until=date2)]
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


def apply_filters_to_queryset(qs: QuerySet, f_org: List[int] = None, f_type: List[int] = None,
                              f_cur: List[int] = None) -> QuerySet:
    """
    Применяем фильтр по организации, типу контракта и валюте к QuerySet

    :param qs:
    :param f_org:
    :param f_type:
    :param f_cur:
    :return:
    """

    if f_org and f_org[0] != '':
        f_org = list(map(int, f_org))
        qs = qs.filter(organization__pk__in=f_org)
    if f_type and f_type[0] != '':
        f_type = list(map(int, f_type))
        qs = qs.filter(type__pk__in=f_type)
    if f_cur and f_cur[0] != '':
        f_cur = list(map(int, f_cur))
        qs = qs.filter(currency__pk__in__=f_cur)

    return qs


def create_link(sum_amount: int, url: str, param_name: str, param_value: str, date: str) -> str:
    """
    Конструируем ссылку с параметрами внутри таблицы, для создания детализации
    :param sum_amount:
    :param url:
    :param param_name:
    :param param_value:
    :param date:
    :return:
    """
    if sum_amount:
        return '<a href="{}">{}</a>'.format(f'{url}?{param_name}={param_value}&date={date}', sum_amount)
    else:
        return '0'


def get_master_table(f_org: List[int], f_type: List[int], f_cur: List[int], dates: List[datetime.datetime],
                     dimensions: List[str], url: str) -> pd.DataFrame:
    """
    Создает датафрейм для мастер таблицы.
    На вход подаются выбранные фильтры, даты и измерения

    :param f_org:
    :param f_type:
    :param f_cur:
    :param dates:
    :param dimensions:
    :param url:
    :return:
    """
    org_master_tbl = None
    ctype_master_tbl = None
    cur_master_tbl = None
    # Это плохо x_x (вложенный цикл + DRY)
    if '1' in dimensions:
        # Organization
        org_master_tbl = pd.DataFrame(index=list(Organization.objects.values_list('organization_name', flat=True)),
                                      columns=[d.strftime('%Y-%m-%d') for d in dates])
        for d in dates:
            d = d.strftime('%Y-%m-%d')
            for org in list(Organization.objects.values_list('organization_name', flat=True)):
                qs = Contract.objects.filter(
                    contract_start_date__lte=d,
                    contract_end_date__gte=d,
                    organization__organization_name=org,
                )
                qs = apply_filters_to_queryset(qs, f_org, f_type, f_cur)
                sum_amount = qs.aggregate(sum_amount=Sum('contract_amount'))['sum_amount']
                org_master_tbl[d][org] = create_link(sum_amount, url, 'org', org, d)
    if '2' in dimensions:
        # ContractType
        ctype_master_tbl = pd.DataFrame(index=list(ContractType.objects.values_list('type_name', flat=True)),
                                        columns=[d.strftime('%Y-%m-%d') for d in dates])
        for d in dates:
            d = d.strftime('%Y-%m-%d')
            for cont_type in list(ContractType.objects.values_list('type_name', flat=True)):
                qs = Contract.objects.filter(
                    contract_start_date__lte=d,
                    contract_end_date__gte=d,
                    type__type_name=cont_type,
                )
                qs = apply_filters_to_queryset(qs, f_org, f_type, f_cur)
                sum_amount = qs.aggregate(sum_amount=Sum('contract_amount'))['sum_amount']
                ctype_master_tbl[d][cont_type] = create_link(sum_amount, url, 'type', cont_type, d)
    if '3' in dimensions:
        # Currency
        cur_master_tbl = pd.DataFrame(index=list(Currency.objects.values_list('name', flat=True)),
                                      columns=[d.strftime('%Y-%m-%d') for d in dates])
        for d in dates:
            d = d.strftime('%Y-%m-%d')
            for cur in list(Currency.objects.values_list('name', flat=True)):
                qs = Contract.objects.filter(
                    contract_start_date__lte=d,
                    contract_end_date__gte=d,
                    currency__name=cur,
                )
                qs = apply_filters_to_queryset(qs, f_org, f_type, f_cur)
                sum_amount = qs.aggregate(sum_amount=Sum('contract_amount'))['sum_amount']
                cur_master_tbl[d][cur] = create_link(sum_amount, url, 'cur', cur, d)

    return pd.concat([org_master_tbl, ctype_master_tbl, cur_master_tbl])


def get_dates(report_type: str, start_date: str, end_date: str) -> List[datetime.datetime]:
    """
    Создает список дат, исходя из начальной и конечной даты
    и типа отчета.

    :param report_type:
    :param start_date:
    :param end_date:
    :return:
    """
    if report_type == '1':
        # monthly
        return get_months_end(start_date, end_date)
    elif report_type == '2':
        # weekly
        return get_weeks_end(start_date, end_date)
    elif report_type == '3':
        # daily
        dates = [d for d in date_range(start_date, end_date)]
        return dates
    else:
        raise Exception('Wrong report type')


def create_detail_queryset(org_par: str, type_par: str, cur_par: str, date_par: str, post_data: dict) -> QuerySet:
    """
    Функция создает QuerySet для таблицы детализации, получая на вход параметры GET запроса
    и значения фильтра
    :param org_par:
    :param type_par:
    :param cur_par:
    :param date_par:
    :param post_data:
    :return:
    """
    detail_qs = Contract.objects.filter(
        contract_start_date__lte=date_par,
        contract_end_date__gte=date_par,
    )

    if org_par:
        detail_qs = detail_qs.filter(organization__organization_name=org_par)

    if type_par:
        detail_qs = detail_qs.filter(type__type_name=type_par)

    if cur_par:
        detail_qs = detail_qs.filter(currency__name=cur_par)


    detail_qs = apply_filters_to_queryset(
        detail_qs,
        post_data['organizations_select'],
        post_data['contract_type_select'],
        post_data['currency_select']
    )
    return detail_qs
