from app.forms import AccountUserForm, BudgetItemForm, RegistrationForm
from app.models import AccountUser, Budget
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse


def home(request):
    if request.user.is_authenticated:
        return redirect('account_home')

    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save account
            user = form.save()

            # Login under new account
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            login(request, user)

            # Go to account home
            return redirect('account_home')
    else:
        form = RegistrationForm()

    ctx = {'form': form}

    return render(request, 'auth/register.html', ctx)


# # # # # # # # # # # # # # # # # # # #
# ALL BELOW SHOULD BE LOGIN REQUIRED  #
# # # # # # # # # # # # # # # # # # # # 

@login_required
def account_home(request):
    users = AccountUser.objects.filter(account=request.user)
    if not users:
        messages.warning(
            request,
            'There are no users associated with your account. '
            'Create users <a href={}>here</a>.'.format(reverse('user_create')),
            extra_tags='safe'
        )

    ctx = {
        'users': users,
    }

    return render(request, 'account/index.html', ctx)


@login_required
def users_list(request):
    account_users = AccountUser.objects.filter(account=request.user)
    if not account_users:
        messages.warning(
            request,
            'There are no users associated with your account. '
            'Create users <a href={}>here</a>.'.format(reverse('user_create'))
        )

    ctx = {
        'account_users': account_users,
    }

    return render(request, 'account/user.html', ctx)


@login_required
def user_create(request):
    if request.method == 'POST':
        form = AccountUserForm(request.POST)
        if form.is_valid():
            account_user = form.save(commit=False)
            account_user.account = request.user
            form.save()
            return redirect('users_list')
        else:
            for error in form.errors:
                messages.error(request, error)

    form = AccountUserForm()
    return render(request, 'account/user_create.html', {'form': form})


@login_required
def budget_list(request):
    budget_items = Budget.objects.filter(account=request.user)
    print(budget_items)
    if not budget_items:
        messages.warning(
            request,
            "You haven't created any budget line items. "
            'Start <a href={}>here</a>.'.format(reverse('budget_create'))
        )

    ctx = {
        'budget_items': budget_items,
    }

    return render(request, 'account/budget.html', ctx)


@login_required
def budget_create(request):
    if request.method == 'POST':
        form = BudgetItemForm(request.POST)
        if form.is_valid():
            budget_item = form.save(commit=False)
            budget_item.account = request.user
            form.save()
            return redirect('budget_list')
        else:
            for error in form.errors:
                messages.error(request, error)

    form = BudgetItemForm()
    return render(request, 'account/budget_create.html', {'form': form})
