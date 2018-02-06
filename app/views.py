from app.forms import AccountUserForm, BudgetItemForm, RegistrationForm, TransactionForm
from app.models import AccountUser, Budget, Transaction
from app.util.calendar import get_current_week, get_local_today_min, get_start_day_for_week
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_out
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.timezone import get_current_timezone, make_aware


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

    start = get_local_today_min()
    today = start.date()

    daily_budget = account.get_daily_goal()
    weekly_standing = account.get_weekly_standing()
    if weekly_standing >= 0:
        weekly_standing = '+' + str(weekly_standing)
        standing_class = 'has-text-success'
    else:
        weekly_standing = str(weekly_standing)
        standing_class = 'has-text-danger'

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
        'weekly_standing': weekly_standing,
        'standing_class': standing_class,
        'remaining': remaining,
        'daily_trans': daily_trans,
        'other_trans': other_trans
    }

    messages.info(request, 'Logged in as {}'.format(account.username), extra_tags='logged_in')

    return render(request, 'account/index.html', ctx)


@login_required
def users_list(request):
    account = request.user
    account_users = AccountUser.objects.filter(account=account)
    if not account_users:
        messages.warning(
            request,
            'There are no users associated with your account. '
            'Create users <a href={}>here</a>.'.format(reverse('user_create'))
        )

    total_income = account_users.aggregate(total=Sum('income'))['total']
    user_count = account_users.count()

    today = get_local_today_min()
    today_count = Transaction.objects.filter(account=account, time__gte=today).count()

    ctx = {
        'account_users': account_users,
        'total_income': total_income,
        'user_count': user_count,
        'today_count': today_count
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
    budget_items = Budget.objects.filter(account=request.user) \
        .exclude(name=Budget.DAILY) \
        .order_by('-value')

    budget_total = budget_items.aggregate(total=Sum('value'))['total']
    budget_count = budget_items.count()

    if not budget_items:
        messages.warning(
            request,
            "You haven't created any budget line items. "
            'Start <a href={}>here</a>.'.format(reverse('budget_create')),
            extra_tags=['safe', 'warning']
        )

    ctx = {
        'budget_items': budget_items,
        'budget_total': budget_total,
        'budget_count': budget_count
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
            messages.success(request, 'Created!', extra_tags='success')
            return redirect('budget_list')
        else:
            for error in form.errors:
                messages.error(request, error)

    form = BudgetItemForm()
    return render(request, 'account/budget_create.html', {'form': form})


@login_required
def budget_delete(request, budget_id):
    Budget.objects.get(id=budget_id).delete()
    messages.success(request, 'Deleted!', extra_tags='success')
    return redirect('budget_list')


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


@login_required
def get_daily_pie_data(request):
    start = get_local_today_min()

    account = request.user
    daily_budget = account.get_daily_goal()
    t_sum = Transaction.objects.filter(
        account=request.user,
        time__gte=start,
        budget__name=Budget.DAILY
    ).aggregate(total=Sum('value'))['total']

    if not t_sum:
        t_sum = 0

    remaining = daily_budget - t_sum

    data = {
        'table_data': [
            ['Spent', t_sum],
            ['Remaining', remaining]
        ]
    }

    return JsonResponse(data)


@login_required
def get_weekly_status_data(request):
    account = request.user
    start_day = get_start_day_for_week()

    week = get_current_week()
    week_days = map(
        lambda x: make_aware(
            datetime(start_day.year, start_day.month, x),
            timezone=get_current_timezone()
        ),
        week
    )

    totals = Transaction.objects.filter(account=account) \
        .filter(time__gte=start_day, budget__name=Budget.DAILY) \
        .annotate(day=TruncDay('time')) \
        .values('day') \
        .annotate(total=Sum('value')) \
        .values('day', 'total') \
        .order_by('day')

    total_days = {item['day']: item['total'] for item in totals}

    data = list()
    for day in week_days:
        if day in total_days:
            data.append([day, total_days[day]])
        else:
            data.append([day, 0])

    return JsonResponse({'data': data})
