from django.forms import ModelForm, ChoiceField, Select
from . import models


class OrgFilter(ModelForm):
    organizations_select = ChoiceField(
        choices=[(org.id, org.organization_name) for org in models.Organization.objects.all()])

    class Meta:
        model = models.Organization
        fields = ('organizations_select',)
        widgets = {
            'organizations_select': Select(attrs={'class': 'select'})
        }

class ContractTypeFilter(ModelForm):
    contract_type_select = ChoiceField(
        choices=[(cont_type.id, cont_type.type_name) for cont_type in models.ContractType.objects.all()])

    class Meta:
        model = models.ContractType
        fields = ('contract_type_select',)
        widgets = {
            'contract_type_select': Select(attrs={'class': 'select'})
        }

class CurrencyFilter(ModelForm):
    currency_select = ChoiceField(
        choices=[(cur.id, cur.name) for cur in models.Currency.objects.all()])

    class Meta:
        model = models.Currency
        fields = ('currency_select',)
        widgets = {
            'currency_select': Select(attrs={'class': 'select'})
        }