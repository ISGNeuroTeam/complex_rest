# Generated by Django 3.2.9 on 2023-06-23 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0004_role_model_api_20230518_1302'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='owner_applicability',
        ),
    ]
