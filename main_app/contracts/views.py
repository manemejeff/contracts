import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Sum

from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter, DatePicker
from .models import Contract, Organization, ContractType, Currency
from .utils import get_months_end, get_weeks_end, date_range, apply_filters_to_queryset, get_master_table, get_dates


# Create your views here.

class Index(View):
    qs = Contract.objects.all()
    detail_tbl = pd.DataFrame.from_records(qs.values())

    def get(self, request):
        master_tbl = None
        # detail_tbl = pd.DataFrame.from_records(Contract.objects.all().values()).to_html()
        context = {
            'org_filter': OrgFilter(),
            'contract_type_filter': ContractTypeFilter(),
            'currency_filter': CurrencyFilter(),
            'detail_tbl': self.detail_tbl.to_html(),
            'date_picker': DatePicker(),
        }
        return render(request, 'contracts/index.html', context=context)

    def post(self, request):
        f_org = None
        f_type = None
        f_cur = None

        # Собираем фильтры по организации, типу, валюте
        # избавиться от обращения к каждому полю, (мб изменить названия чтоб их можно было маппить на дф)
        print(request.POST)
        if request.POST['organizations_select']:
            f_org = list(map(int, request.POST.getlist('organizations_select')))
            # print(Organization.objects.get(pk=f_org))

        if request.POST['contract_type_select']:
            f_type = list(map(int, request.POST.getlist('contract_type_select')))

        if request.POST['currency_select']:
            f_cur = list(map(int, request.POST.getlist('currency_select')))

        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        report_type = request.POST['report_type']
        dimensions = request.POST.getlist('dimensions')
        # print(dimensions)

        # Фильтруем по организации, типу, валюте
        if f_org:
            self.detail_tbl = self.detail_tbl[self.detail_tbl.organization_id.isin(f_org)]
        if f_type:
            self.detail_tbl = self.detail_tbl[self.detail_tbl.type_id.isin(f_type)]
        if f_cur:
            self.detail_tbl = self.detail_tbl[self.detail_tbl.currency_id.isin(f_cur)]

        dates = get_dates(report_type, start_date, end_date)
        # if report_type == '1':
        #     # monthly
        #     dates = get_months_end(start_date, end_date)
        # elif report_type == '2':
        #     # weekly
        #     dates = get_weeks_end(start_date, end_date)
        # elif report_type == '3':
        #     # daily
        #     dates = [d for d in date_range(start_date, end_date)]
        # else:
        #     raise Exception('Wrong report type')

        master_tbl = get_master_table(f_org, f_type, f_cur, dates, dimensions)

        context = {
            'org_filter': OrgFilter(request.POST),
            'contract_type_filter': ContractTypeFilter(request.POST),
            'currency_filter': CurrencyFilter(request.POST),
            'detail_tbl': self.detail_tbl.to_html(),
            'date_picker': DatePicker(request.POST),
            'master_tbl': master_tbl.to_html(),
        }

        return render(request, 'contracts/index.html', context=context)
