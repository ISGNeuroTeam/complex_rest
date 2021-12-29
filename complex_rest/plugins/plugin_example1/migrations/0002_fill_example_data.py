from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Person = apps.get_model('plugin_example1', 'Person')
    db_alias = schema_editor.connection.alias
    Person.objects.using(db_alias).bulk_create([
        Person(name='Artem', is_active=True),
        Person(name='Alexandr', is_active=True),
        Person(name='Andrey', is_active=True),
        Person(name='Egor', is_active=True)
    ])


def reverse_func(apps, schema_editor):
    # forwards_func() creates  instances,
    # so reverse_func() should delete them.
    Person = apps.get_model('plugin_example1', 'Person')
    db_alias = schema_editor.connection.alias
    Person.objects.using(db_alias).filter(name='Artem').delete()
    Person.objects.using(db_alias).filter(name='Alexandr').delete()
    Person.objects.using(db_alias).filter(name='Andrey').delete()
    Person.objects.using(db_alias).filter(name='Egor').delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('plugin_example1', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
