import pandas as pd
from django.shortcuts import render
from .forms import OrgFilter, ContractTypeFilter, CurrencyFilter
from .models import Contract

# Create your views here.

def index(request):
    tbl = pd.DataFrame.from_records(Contract.objects.all().values()).to_html()
    context = {
        'org_filter': OrgFilter(),
        'contract_type_filter': ContractTypeFilter(),
        'currency_filter': CurrencyFilter(),
        'tbl': tbl,
    }
    return render(request, 'contracts/index.html', context=context)
