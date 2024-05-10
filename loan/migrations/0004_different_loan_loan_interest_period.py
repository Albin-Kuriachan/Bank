# Generated by Django 5.0.4 on 2024-05-08 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0003_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Different_Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Loan_Interest_Period',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_interest', models.IntegerField()),
                ('loan_period', models.IntegerField()),
                ('loan_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.different_loan')),
            ],
        ),
    ]