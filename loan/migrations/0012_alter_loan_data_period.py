# Generated by Django 5.0.4 on 2024-05-09 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0011_alter_loan_data_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan_data',
            name='period',
            field=models.IntegerField(),
        ),
    ]