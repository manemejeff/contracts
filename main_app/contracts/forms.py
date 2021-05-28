from django.forms import ModelForm, ChoiceField, Select, MultipleChoiceField, SelectMultiple
from . import models

blank_choice = [('', '---------'), ]


class OrgFilter(ModelForm):
    organizations_select = MultipleChoiceField(
        choices=blank_choice + [(org.id, org.organization_name) for org in models.Organization.objects.all()],
        initial='',
        required=False,
    )


    class Meta:
        model = models.Organization
        fields = ('organizations_select',)
        widgets = {
            'organizations_select': SelectMultiple(attrs={'class': 'select'})
        }


class ContractTypeFilter(ModelForm):
    contract_type_select = MultipleChoiceField(
        choices=blank_choice + [(cont_type.id, cont_type.type_name) for cont_type in models.ContractType.objects.all()],
        initial='',
        required=False,
    )

    class Meta:
        model = models.ContractType
        fields = ('contract_type_select',)
        widgets = {
            'contract_type_select': SelectMultiple(attrs={'class': 'select'})
        }


class CurrencyFilter(ModelForm):
    currency_select = MultipleChoiceField(
        choices=blank_choice + [(cur.id, cur.name) for cur in models.Currency.objects.all()],
        initial='',
        required=False
    )

    class Meta:
        model = models.Currency
        fields = ('currency_select',)
        widgets = {
            'currency_select': SelectMultiple(attrs={'class': 'select'})
        }
