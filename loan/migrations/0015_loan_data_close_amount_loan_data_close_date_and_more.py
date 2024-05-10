# Generated by Django 5.0.4 on 2024-05-09 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0014_alter_loan_data_to_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan_data',
            name='close_amount',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='loan_data',
            name='close_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='loan_data',
            name='from_account',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='loan_data',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('CLOSED', 'Closed')], default='ACTIVE', max_length=10),
        ),
    ]
