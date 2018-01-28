from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


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
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Budget(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14)

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    user = models.ForeignKey(AccountUser, on_delete=models.SET_NULL, null=True)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=128)
    value = models.DecimalField(decimal_places=2, max_digits=14)
    time = models.DateTimeField(auto_now_add=True)
