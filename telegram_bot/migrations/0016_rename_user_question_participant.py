# Generated by Django 4.0.4 on 2022-08-06 23:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0015_alter_question_options_remove_block_speaker_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='user',
            new_name='participant',
        ),
    ]
