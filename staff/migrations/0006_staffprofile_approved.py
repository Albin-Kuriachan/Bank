# Generated by Django 5.0.4 on 2024-05-10 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_alter_staffprofile_personal_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffprofile',
            name='approved',
            field=models.BooleanField(default=True),
        ),
    ]
