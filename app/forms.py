from app.models import Account, AccountUser, Budget, Transaction
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


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'budget', 'description', 'value']

    def __init__(self, account, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(queryset=AccountUser.objects.filter(account=account))
        self.fields['budget'] = forms.ModelChoiceField(queryset=Budget.objects.filter(account=account))
