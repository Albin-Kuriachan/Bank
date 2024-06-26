# Generated by Django 5.0.4 on 2024-05-06 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixed_deposit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interest_Table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='fd_account_model',
            name='tenure',
            field=models.IntegerField(default=0),
        ),
    ]
