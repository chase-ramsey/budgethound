from app.forms import AccountUserForm, BudgetItemForm, RegistrationForm, TransactionForm
from app.models import AccountUser, Budget, Transaction
from datetime import datetime, time
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.db.models import Sum
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.utils.timezone import get_current_timezone, localtime, make_aware, now


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


@receiver(user_logged_out)
def on_logout(sender, request, **kwargs):
    messages.info(request, 'Successfully logged out', extra_tags='success')


# # # # # # # # # # # # # # # # # # # #
# ALL BELOW SHOULD BE LOGIN REQUIRED  #
# # # # # # # # # # # # # # # # # # # # 

@login_required
def account_home(request):
    account = request.user
    if not Budget.objects.filter(account=account, name=Budget.DAILY).exists():
        Budget.objects.create(account=account, name=Budget.DAILY, description=Budget.DAILY_DESC)
    users = AccountUser.objects.filter(account=account)
    if not users:
        messages.warning(
            request,
            'There are no users associated with your account. '
            'Create users <a href={}>here</a>.'.format(reverse('user_create')),
            extra_tags=['safe', 'warning']
        )

    start = make_aware(datetime.combine(localtime(now()), time.min), \
        timezone=get_current_timezone())

    today = start.date()

    daily_budget = account.get_daily_goal()
    daily_trans = Transaction.objects.filter(
        account=request.user,
        time__gte=start,
        budget__name=Budget.DAILY
    ).order_by('-time')

    if daily_trans:
        t_sum = daily_trans.aggregate(total=Sum('value'))['total']
        remaining = daily_budget - t_sum
    else:
        remaining = daily_budget

    other_trans = Transaction.objects.filter(account=request.user, time__gte=start) \
        .exclude(budget__name=Budget.DAILY) \
        .order_by('-time')

    ctx = {
        'users': users,
        'today': today,
        'daily_budget': daily_budget,
        'remaining': remaining,
        'daily_trans': daily_trans,
        'other_trans': other_trans
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
    budget_items = Budget.objects.filter(account=request.user).exclude(name=Budget.DAILY)
    if not budget_items:
        messages.warning(
            request,
            "You haven't created any budget line items. "
            'Start <a href={}>here</a>.'.format(reverse('budget_create')),
            extra_tags=['safe', 'warning']
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


@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = request.user
            form.save()
            return redirect('account_home')
        else:
            for error in form.errors:
                messages.error(request, error)

    form = TransactionForm(request.user)
    return render(request, 'account/transaction_create.html', {'form': form})
