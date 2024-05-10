from django.db import models
from user.models import Profile

# Create your models here.



class Loan_data(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    loan_account_number = models.CharField(max_length=20, unique=True)
    loan_name = models.CharField(max_length=20,null=True, blank=True)
    interest_rate = models.IntegerField(null=True, blank=True)
    period = models.IntegerField()
    loan_amount = models.IntegerField()
    emi = models.IntegerField(null=True, blank=True)
    open_date = models.DateField(auto_now_add=True,null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_amount = models.FloatField(null=True, blank=True)
    to_account =models.CharField(max_length=10)
    current_balance = models.IntegerField(null=True, blank=True)
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    close_date = models.DateField(null=True, blank=True)
    close_amount = models.FloatField(null=True, blank=True)
    from_account =models.CharField(max_length=10,null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} {self.loan_name}"
class Different_Loan(models.Model):
    loan_name = models.CharField(max_length=20)

    def __str__(self):
        return self.loan_name
class Loan_Interest_Period(models.Model):
    loan_name = models.ForeignKey(Different_Loan,on_delete=models.CASCADE)
    amount_limit=models.CharField(max_length=20,null=True, blank=True)
    loan_interest = models.IntegerField()
    loan_period = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.loan_name} {self.loan_interest}% {self.loan_period}"







