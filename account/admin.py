from django.contrib import admin
from .models import Savings_account, Transaction


# class SavingsAccountAdmin(admin.ModelAdmin):
#     list_display = ('user', 'account_number', 'balance')
#
#
# admin.site.register(Savings_account, SavingsAccountAdmin)


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0

    ordering = ['-id']

@admin.register(Savings_account)
class SavingAdmin(admin.ModelAdmin):
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'saving_account', 'account', 'amount', 'balance', 'date', 'type', 'transaction_id')
    list_filter = ('customer', 'saving_account', 'date', 'type')
    search_fields = ('customer__username', 'saving_account__account_number', 'transaction_id')
    date_hierarchy = 'date'
