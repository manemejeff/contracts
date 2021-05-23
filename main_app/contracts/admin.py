from django.contrib import admin
from .models import Contract, ContractType, Organization, Currency

# Register your models here.

admin.site.register(Contract)
admin.site.register(ContractType)
admin.site.register(Organization)
admin.site.register(Currency)