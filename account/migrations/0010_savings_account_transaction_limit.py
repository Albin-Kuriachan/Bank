# Generated by Django 5.0.4 on 2024-05-08 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_remove_transaction_payer_account_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='savings_account',
            name='transaction_limit',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
