from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    def get_daily_goal(self):
        """
        Calculate and return the allowed spending amount per day for the account
        """
        pass


class AccountUser(models.Model):
    class Meta:
        unique_together = ('name', 'account')

    name = models.CharField(max_length=64)
    income = models.DecimalField(decimal_places=2, max_digits=14)  # lol max_digits
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_users')

    def __str__(self):
        return '{} ({})'.format(self.name, self.account_id)


class Budget(models.Model):
    class Meta:
        unique_together = ('name', 'account')

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='budget_lines')
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14)

    def __str__(self):
        return '{} ({})'.format(self.name, self.value)


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(AccountUser, on_delete=models.SET_NULL, null=True, related_name='transactions')
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, related_name='transactions')
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} ({})'.format(self.name, self.value)
