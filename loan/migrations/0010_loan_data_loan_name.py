# Generated by Django 5.0.4 on 2024-05-09 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0009_loan_data_emi'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan_data',
            name='loan_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]