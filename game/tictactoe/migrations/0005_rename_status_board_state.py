# Generated by Django 5.0.3 on 2024-03-29 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tictactoe', '0004_alter_board_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='board',
            old_name='status',
            new_name='state',
        ),
    ]
