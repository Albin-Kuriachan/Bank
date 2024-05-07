from django.db import models
from user.models import Profile


class FD_Account_Model(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    interest_rate = models.IntegerField(null=True, blank=True)
    tenure = models.CharField(max_length=20,null=True, blank=True)
    deposit_amount = models.IntegerField()
    interest_period = models.CharField(max_length=20,null=True, blank=True)
    open_date = models.DateField(auto_now_add=True,null=True, blank=True)
    maturity_date = models.DateField(null=True, blank=True)
    maturity_amount = models.FloatField(null=True, blank=True)
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    close_date = models.DateField(null=True, blank=True)
    close_amount = models.FloatField(null=True, blank=True)
    current_balance = models.IntegerField(null=True, blank=True)



    def __str__(self):
        return self.user.first_name + " " + self.account_number
class Interest_Table(models.Model):
    interest=models.PositiveIntegerField(null=True, blank=True)
    period=models.CharField(max_length=20,null=True, blank=True)


