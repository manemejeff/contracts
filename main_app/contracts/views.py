import json

import pandas as pd
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter, DatePicker
from .models import Contract
from .utils import get_master_table, get_dates


# Create your views here.

class Index(View):
    # qs = Contract.objects.all()
    detail_tbl = None
    master_tbl = None
    post_data = None
    f_org = None
    f_type = None
    f_cur = None

    def get(self, request):
        master_tbl = None


        if request.session['master_tbl']:
            master_tbl = pd.read_json(request.session['master_tbl'], orient='split')
        print()

        context = {
            'org_filter': OrgFilter(request.session['post_data']),
            'contract_type_filter': ContractTypeFilter(request.session['post_data']),
            'currency_filter': CurrencyFilter(request.session['post_data']),
            'detail_tbl': self.detail_tbl.to_html() if self.detail_tbl else '',
            'date_picker': DatePicker(request.session['post_data']),
            'master_tbl': master_tbl.to_html(escape=False),
        }
        return render(request, 'contracts/index.html', context=context)

    def post(self, request):

        request.session['post_data'] = {}
        request.session['post_data']['organizations_select'] = request.POST.getlist('organizations_select')
        request.session['post_data']['contract_type_select'] = request.POST.getlist('contract_type_select')
        request.session['post_data']['currency_select'] = request.POST.getlist('currency_select')

        request.session['post_data']['start_date'] = request.POST['start_date']
        request.session['post_data']['end_date'] = request.POST['end_date']
        request.session['post_data']['report_type'] = request.POST['report_type']
        request.session['post_data']['dimensions'] = request.POST.getlist('dimensions')
        # Собираем фильтры по организации, типу, валюте
        # избавиться от обращения к каждому полю, (мб изменить названия чтоб их можно было маппить на дф)
        # print(dir(request))
        if request.POST['organizations_select']:
            self.f_org = list(map(int, request.POST.getlist('organizations_select')))
            # print(Organization.objects.get(pk=f_org))

        if request.POST['contract_type_select']:
            self.f_type = list(map(int, request.POST.getlist('contract_type_select')))

        if request.POST['currency_select']:
            self.f_cur = list(map(int, request.POST.getlist('currency_select')))

        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        report_type = request.POST['report_type']
        dimensions = request.POST.getlist('dimensions')
        # print(dimensions)

        # Фильтруем по организации, типу, валюте
        # if f_org:
        #     self.detail_tbl = self.detail_tbl[self.detail_tbl.organization_id.isin(f_org)]
        # if f_type:
        #     self.detail_tbl = self.detail_tbl[self.detail_tbl.type_id.isin(f_type)]
        # if f_cur:
        #     self.detail_tbl = self.detail_tbl[self.detail_tbl.currency_id.isin(f_cur)]

        dates = get_dates(report_type, start_date, end_date)
        master_tbl = get_master_table(self.f_org, self.f_type, self.f_cur, dates, dimensions, request.build_absolute_uri(reverse('index')))
        request.session['master_tbl'] = master_tbl.to_json(orient='split')

        context = {
            'org_filter': OrgFilter(request.POST),
            'contract_type_filter': ContractTypeFilter(request.POST),
            'currency_filter': CurrencyFilter(request.POST),
            # 'detail_tbl': self.detail_tbl.to_html(),
            'date_picker': DatePicker(request.POST),
            'master_tbl': master_tbl.to_html(escape=False),
        }

        return render(request, 'contracts/index.html', context=context)


