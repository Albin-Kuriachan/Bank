# Generated by Django 5.0.4 on 2024-05-10 05:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_alter_customuser_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='user',
            new_name='customer_id',
        ),
    ]
