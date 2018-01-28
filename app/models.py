from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Account(AbstractBaseUser, PermissionsMixin):
    # Email field adapted directly from AbstractUser.username field in Django docs
    email = models.CharField(_('email'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid email. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that email already exists."),
        })

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_daily_goal(self):
        """
        Calculate and return the allowed spending amount per day for the account
        """
        pass


class AccountUser(models.Model):
    name = models.CharField(max_length=64)
    income = models.DecimalField(decimal_places=2, max_digits=14)  # lol max_digits
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_users')


class Budget(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='budget_lines')
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14)

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(AccountUser, on_delete=models.SET_NULL, null=True, related_name='transactions')
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, related_name='transactions')
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14)
    time = models.DateTimeField(auto_now_add=True)
