# Generated by Django 5.0.4 on 2024-05-07 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixed_deposit', '0014_fd_account_model_close_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fd_account_model',
            name='current_balance',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
