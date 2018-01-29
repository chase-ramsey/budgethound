from app.models import Account, AccountUser, Budget
from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegistrationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['username', 'password1', 'password2']

    username = forms.EmailField(label="Email")


class AccountUserForm(forms.ModelForm):
    class Meta:
        model = AccountUser
        fields = ['name', 'income']


class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'description', 'value']
