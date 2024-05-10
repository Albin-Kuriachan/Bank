# Generated by Django 5.0.4 on 2024-05-10 07:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_alter_staffprofile_personal_email'),
        ('user', '0011_rename_user_customuser_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='staff_id',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.staffprofile'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='customer_id',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='user.profile'),
        ),
    ]
