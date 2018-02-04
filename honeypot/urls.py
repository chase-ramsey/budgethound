from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from app.views import (
    home, 
    account_home,
    budget_list,
    budget_create,
    get_daily_pie_data,
    get_weekly_status_data,
    register, 
    transaction_create,
    user_create, 
    users_list
)


urlpatterns = [
    path('', home, name='home'),
    path('account/', account_home, name='account_home'),
    path('account/users/', users_list, name='users_list'),
    path('account/users/create/', user_create, name='user_create'),
    path('account/budget/', budget_list, name='budget_list'),
    path('account/budget/create/', budget_create, name='budget_create'),
    path('account/transaction/create/', transaction_create, name='transaction_create'),
    path('account/daily_pie', get_daily_pie_data, name='daily_pie_ajax'),
    path('account/weekly_status', get_weekly_status_data, name='weekly_status_ajax'),
    path('login/', auth_views.login, {'template_name': 'auth/login.html'}, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/login'}, name='logout'),
    path('register/', register, name='register'),
    path('admin/', admin.site.urls)
]
