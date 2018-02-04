from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    def get_daily_goal(self):
        """
        Calculate and return the allowed spending amount per day for the account
        """
        combined_income = AccountUser.objects.filter(account=self).aggregate(total=models.Sum('income'))
        budget_total = Budget.objects.filter(account=self).aggregate(total=models.Sum('value'))
        try:
            exact = (combined_income['total'] - budget_total['total']) / 32
            return Decimal(format(exact.__floor__(), '.2f'))
        except TypeError:
            return Decimal('0.00')


class AccountUser(models.Model):
    class Meta:
        unique_together = ('name', 'account')

    name = models.CharField(max_length=64)
    income = models.DecimalField(decimal_places=2, max_digits=14)  # lol max_digits
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_users')

    def __str__(self):
        return self.name


class Budget(models.Model):
    DAILY = 'Daily'
    DAILY_DESC =  'Daily spending allowance'

    class Meta:
        unique_together = ('name', 'account')

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='budget_lines')
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14, null=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(AccountUser, on_delete=models.SET_NULL, null=True, related_name='transactions')
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, related_name='transactions')
    description = models.CharField(max_length=128, blank=True)
    value = models.DecimalField(decimal_places=2, max_digits=14)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({})'.format(self.value, self.account)
