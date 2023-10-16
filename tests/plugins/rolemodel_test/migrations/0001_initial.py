# Generated by Django 3.2.9 on 2023-10-16 08:29

from django.db import migrations, models
import rest_auth.models.abc
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PluginKeychain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('_name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('_zone', models.IntegerField(blank=True, null=True)),
                ('_auth_objects', models.TextField(default='')),
            ],
            options={
                'abstract': False,
            },
            bases=(rest_auth.models.abc.IKeyChain, models.Model),
        ),
        migrations.CreateModel(
            name='PluginKeychainUUID',
            fields=[
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('_name', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('_zone', models.IntegerField(blank=True, null=True)),
                ('_auth_objects', models.TextField(default='')),
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(rest_auth.models.abc.IKeyChain, models.Model),
        ),
        migrations.CreateModel(
            name='SomePluginAuthCoveredModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('_owner_id', models.UUIDField(default=uuid.uuid4, editable=False, null=True, unique=True)),
                ('_keychain_id', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(rest_auth.models.abc.IAuthCovered, models.Model),
        ),
        migrations.CreateModel(
            name='SomePluginAuthCoveredModelUUID',
            fields=[
                ('name', models.CharField(max_length=255)),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('_owner_id', models.UUIDField(default=uuid.uuid4, editable=False, null=True, unique=True)),
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('_keychain_id', models.UUIDField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(rest_auth.models.abc.IAuthCovered, models.Model),
        ),
    ]
