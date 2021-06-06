
import pandas as pd
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter, DatePicker
from .utils import get_master_table, get_dates, create_detail_queryset


# Create your views here.

class Index(View):

    def get(self, request):

        if request.session['master_tbl']:
            master_tbl = pd.read_json(request.session['master_tbl'], orient='split')
            master_tbl = master_tbl.rename(columns=lambda x: x.strftime('%Y-%m-%d'))

        context = {
            'org_filter': OrgFilter(request.session['post_data']),
            'contract_type_filter': ContractTypeFilter(request.session['post_data']),
            'currency_filter': CurrencyFilter(request.session['post_data']),
            'date_picker': DatePicker(request.session['post_data']),
            'master_tbl': master_tbl.to_html(escape=False),
        }

        org_par = request.GET.get('org', '')
        type_par = request.GET.get('type', '')
        cur_par = request.GET.get('cur', '')
        date_par = request.GET.get('date', '')

        if date_par:
            context['detail_tbl'] = create_detail_queryset(org_par, type_par, cur_par, date_par,
                                                           request.session['post_data'])

        return render(request, 'contracts/index.html', context=context)

    def post(self, request):

        f_org = None
        f_type = None
        f_cur = None

        request.session['post_data'] = {}
        request.session['post_data']['organizations_select'] = request.POST.getlist('organizations_select')
        request.session['post_data']['contract_type_select'] = request.POST.getlist('contract_type_select')
        request.session['post_data']['currency_select'] = request.POST.getlist('currency_select')

        request.session['post_data']['start_date'] = request.POST['start_date']
        request.session['post_data']['end_date'] = request.POST['end_date']
        request.session['post_data']['report_type'] = request.POST['report_type']
        request.session['post_data']['dimensions'] = request.POST.getlist('dimensions')

        # Собираем фильтры по организации, типу, валюте
        # хочу избавиться от обращения к каждому полю, (мб изменить названия чтоб их можно было маппить на дф)
        if request.POST['organizations_select']:
            f_org = list(map(int, request.POST.getlist('organizations_select')))

        if request.POST['contract_type_select']:
            f_type = list(map(int, request.POST.getlist('contract_type_select')))

        if request.POST['currency_select']:
            f_cur = list(map(int, request.POST.getlist('currency_select')))

        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        report_type = request.POST['report_type']
        dimensions = request.POST.getlist('dimensions')

        dates = get_dates(report_type, start_date, end_date)
        master_tbl = get_master_table(f_org, f_type, f_cur, dates, dimensions,
                                      request.build_absolute_uri(reverse('index')))
        request.session['master_tbl'] = master_tbl.to_json(orient='split')

        context = {
            'org_filter': OrgFilter(request.POST),
            'contract_type_filter': ContractTypeFilter(request.POST),
            'currency_filter': CurrencyFilter(request.POST),
            'date_picker': DatePicker(request.POST),
            'master_tbl': master_tbl.to_html(escape=False),
        }

        return render(request, 'contracts/index.html', context=context)
