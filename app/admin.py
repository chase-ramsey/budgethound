from django.contrib import admin
from app.models import Account, AccountUser, Budget, Transaction


admin.site.register(Account)
admin.site.register(AccountUser)
admin.site.register(Budget)
admin.site.register(Transaction)
