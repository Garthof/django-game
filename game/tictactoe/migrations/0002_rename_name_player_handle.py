# Generated by Django 5.0.3 on 2024-03-29 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoe', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='name',
            new_name='handle',
        ),
    ]
