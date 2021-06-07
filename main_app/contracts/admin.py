from django.contrib import admin
from .models import Contract, ContractType, Organization, Currency
import random

# Register your models here.

admin.site.register(Contract)
admin.site.register(ContractType)
admin.site.register(Organization)
admin.site.register(Currency)


# @admin.action(description='Create 10 contracts in db with random data')
# def create_10_contracts_random():
#     c = Contract(
#         organization=random.choice(Organization.objects.all()),
#         type=random.choice(ContractType.objects.all()),
#         currency=random.choice(Currency.objects.all()),
#         contract_start_date='',
#         contract_end_date='',
#         contract_amount=''
#     )
