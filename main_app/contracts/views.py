import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from django.forms import DateField

from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter, DatePicker
from .models import Contract, Organization


# Create your views here.

class Index(View):

    def get(self, request):
        master_tbl = None
        detail_tbl = pd.DataFrame.from_records(Contract.objects.all().values()).to_html()
        context = {
            'org_filter': OrgFilter(),
            'contract_type_filter': ContractTypeFilter(),
            'currency_filter': CurrencyFilter(),
            'detail_tbl': detail_tbl,
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

        detail_tbl = pd.DataFrame.from_records(Contract.objects.all().values())

        # Фильтруем по организации, типу, валюте
        if f_org:
            detail_tbl = detail_tbl[detail_tbl.organization_id.isin(f_org)]
        if f_type:
            detail_tbl = detail_tbl[detail_tbl.type_id.isin(f_type)]
        if f_cur:
            detail_tbl = detail_tbl[detail_tbl.currency_id.isin(f_cur)]

        context = {
            'org_filter': OrgFilter(request.POST),
            'contract_type_filter': ContractTypeFilter(request.POST),
            'currency_filter': CurrencyFilter(request.POST),
            'detail_tbl': detail_tbl.to_html(),
            'date_picker': DatePicker(request.POST),
        }

        return render(request, 'contracts/index.html', context=context)
