# Generated by Django 5.0.4 on 2024-05-09 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0004_different_loan_loan_interest_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan_interest_period',
            name='loan_period',
            field=models.CharField(max_length=10),
        ),
    ]
