import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from django.forms import DateField

from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter, DatePicker
from .models import Contract, Organization, ContractType, Currency
from .utils import get_months_end, get_weeks_end, date_range


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
        # TODO избавиться от обращения к каждому полю, (мб изменить названия чтоб их можно было маппить на дф)
        print(request.POST)
        # print(self.qs)
        if request.POST['organizations_select']:
            f_org = list(map(int, request.POST.getlist('organizations_select')))
            # print(Organization.objects.get(pk=f_org))
            print(f_org)

        if request.POST['contract_type_select']:
            f_type = list(map(int, request.POST.getlist('contract_type_select')))
            print(f_type)

        if request.POST['currency_select']:
            f_cur = list(map(int, request.POST.getlist('currency_select')))
            print(f_cur)

        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        report_type = request.POST['report_type']
        dimensions = request.POST.getlist('dimensions')
        print(dimensions)

        # detail_tbl = pd.DataFrame.from_records(Contract.objects.all().values())

        # Фильтруем по организации, типу, валюте
        if f_org:
            self.detail_tbl = self.detail_tbl[self.detail_tbl.organization_id.isin(f_org)]
        if f_type:
            self.detail_tbl = self.detail_tbl[self.detail_tbl.type_id.isin(f_type)]
        if f_cur:
            self.detail_tbl = self.detail_tbl[self.detail_tbl.currency_id.isin(f_cur)]

        dates = None
        if report_type == '1':
            # monthly
            dates = get_months_end(start_date, end_date)
        elif report_type == '2':
            # weekly
            dates = get_weeks_end(start_date, end_date)
        elif report_type == '3':
            # daily
            dates = [d for d in date_range(start_date, end_date)]
        else:
            raise Exception('Wrong report type')

        org_master_tbl = None
        ctype_master_tbl = None
        cur_master_tbl = None
        # I bet there is a better way x_x
        if '1' in dimensions:
            # Organization
            org_master_tbl = pd.DataFrame(index=list(Organization.objects.all()), columns=[d.strftime('%Y-%m-%d') for d in dates])
            print(org_master_tbl)
        if '2' in dimensions:
            # ContractType
            ctype_master_tbl = pd.DataFrame(index=list(ContractType.objects.all()), columns=[d.strftime('%Y-%m-%d') for d in dates])
        if '3' in dimensions:
            # Currency
            cur_master_tbl = pd.DataFrame(index=list(Currency.objects.all()), columns=[d.strftime('%Y-%m-%d') for d in dates])

        master_tbl = pd.concat([org_master_tbl, ctype_master_tbl, cur_master_tbl])
        print(master_tbl)

        context = {
            'org_filter': OrgFilter(request.POST),
            'contract_type_filter': ContractTypeFilter(request.POST),
            'currency_filter': CurrencyFilter(request.POST),
            'detail_tbl': self.detail_tbl.to_html(),
            'date_picker': DatePicker(request.POST),
        }

        return render(request, 'contracts/index.html', context=context)
