# Generated by Django 5.0.4 on 2024-05-08 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixed_deposit', '0016_alter_fd_account_model_close_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fd_account_model',
            name='from_account',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
