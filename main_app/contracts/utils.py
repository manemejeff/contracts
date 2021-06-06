import datetime
from dateutil.rrule import rrule, MONTHLY, WEEKLY, SU
import calendar
from typing import Optional, List

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

    if f_org:
        qs = qs.filter(organization__pk__in=f_org)
    if f_type:
        qs = qs.filter(type__pk__in=f_type)
    if f_cur:
        qs = qs.filter(currency__in__=f_cur)

    return qs


def get_master_table(f_org: List[int], f_type: List[int], f_cur: List[int], dates: List[datetime.datetime],
                     dimensions: List[str], url: str) -> pd.DataFrame:
    org_master_tbl = None
    ctype_master_tbl = None
    cur_master_tbl = None
    # print(url)
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
                if sum_amount:
                    org_master_tbl[d][org] = '<a href="{}">{}</a>'.format(f'{url}?org={org}&date={d}', sum_amount)
                    print(org_master_tbl)
                else:
                    org_master_tbl[d][org] = 0
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
                ctype_master_tbl[d][cont_type] = qs.aggregate(sum_amount=Sum('contract_amount'))['sum_amount']
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
                cur_master_tbl[d][cur] = qs.aggregate(sum_amount=Sum('contract_amount'))['sum_amount']

    return pd.concat([org_master_tbl, ctype_master_tbl, cur_master_tbl])


def get_dates(report_type: str, start_date: str, end_date: str) -> List[datetime.datetime]:
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


if __name__ == '__main__':
    # get_months_end('2021-03-2', '2021-05-25')
    get_weeks_end('2021-03-2', '2021-05-25')
