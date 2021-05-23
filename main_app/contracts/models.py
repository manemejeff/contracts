from datetime import date
from django.db import models


# Create your models here.
class Organization(models.Model):
    organization_name = models.CharField(max_length=50)

    def __str__(self):
        return self.organization_name


class ContractType(models.Model):
    type_name = models.CharField(max_length=50)

    def __str__(self):
        return self.type_name

class Currency(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Contract(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    type = models.ForeignKey(to=ContractType, on_delete=models.CASCADE)
    currency = models.ForeignKey(to=Currency, on_delete=models.CASCADE)
    contract_start_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=date.today
    )
    contract_end_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=date.today
    )
    contract_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Контракт {self.organization.organization_name} на сумму {self.contract_amount} {self.currency.symbol}"