# Generated by Django 5.0.4 on 2024-05-10 05:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_alter_profile_aadhaar_alter_profile_dob_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user',
            field=models.OneToOneField(default=2, on_delete=django.db.models.deletion.CASCADE, to='user.profile'),
            preserve_default=False,
        ),
    ]
