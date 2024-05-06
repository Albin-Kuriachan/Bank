from django.contrib import admin

from .models import FD_Account_Model,Interest_Table


# Register your models here.

#
# @admin.register(FD_Account_Model)
# class SavingAdmin(admin.ModelAdmin):
#     # inlines = [TransactionInline]

admin.site.register(FD_Account_Model)
admin.site.register(Interest_Table)
