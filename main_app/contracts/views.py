import pandas as pd
from django.shortcuts import render, redirect
from django.views import View

from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter
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
        }
        return render(request, 'contracts/index.html', context=context)

    def post(self, request):
        f_org = list(map(int, request.POST.getlist('organizations_select')))
        # print(Organization.objects.get(pk=f_org))
        print(f_org)
        detail_tbl = pd.DataFrame.from_records(Contract.objects.all().values())
        # print(detail_tbl)
        detail_tbl = detail_tbl[detail_tbl.organization_id.isin(f_org)]
        # print(detail_tbl)

        context = {
            'org_filter': OrgFilter(),
            'contract_type_filter': ContractTypeFilter(),
            'currency_filter': CurrencyFilter(),
            'detail_tbl': detail_tbl.to_html(),
        }

        return render(request, 'contracts/index.html', context=context)
