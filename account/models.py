from django.db import models
from user.models import Profile


class Savings_account(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return self.user.first_name + " " + self.account_number


class Transaction(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE,null=True)
    saving_account = models.ForeignKey(Savings_account, on_delete=models.CASCADE)
    account = models.IntegerField(null=True)
    amount = models.IntegerField()
    balance = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=2)
    transaction_id = models.IntegerField()

    def __str__(self):
        return self.saving_account.user.first_name + " " + self.saving_account.user.last_name + " " + self.saving_account.account_number

    class Meta:
        ordering = ['-date']
