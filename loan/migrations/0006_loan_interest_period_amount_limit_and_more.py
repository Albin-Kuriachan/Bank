# Generated by Django 5.0.4 on 2024-05-09 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0005_alter_loan_interest_period_loan_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan_interest_period',
            name='amount_limit',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='loan_interest_period',
            name='loan_period',
            field=models.CharField(max_length=20),
        ),
    ]
