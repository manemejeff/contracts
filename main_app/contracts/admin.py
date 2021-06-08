from django.contrib import admin
from .models import Contract, ContractType, Organization, Currency
import random
import time


# Register your models here.


def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%Y-%m-%d', prop)


class ContractAdmin(admin.ModelAdmin):
    actions = ['create_10_contracts_random']

    @admin.action(description='Create 10 contracts in db with random data')
    def create_10_contracts_random(self, request, queryset):

        for i in range(10):
            start_date = random_date("2021-01-01", "2021-12-1", random.random())
            end_date = random_date(start_date, "2021-12-31", random.random())
            c = Contract(
                organization=random.choice(Organization.objects.all()),
                type=random.choice(ContractType.objects.all()),
                currency=random.choice(Currency.objects.all()),
                contract_start_date=start_date,
                contract_end_date=end_date,
                contract_amount=random.randrange(1000, 90_000_000, 1000)
            )
            c.save()


admin.site.register(Contract, ContractAdmin)
admin.site.register(ContractType)
admin.site.register(Organization)
admin.site.register(Currency)
