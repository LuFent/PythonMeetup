# Generated by Django 4.0.4 on 2022-08-04 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0003_rename_user_botuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='company_postion',
            field=models.TextField(blank=True, verbose_name='Комания и должность'),
        ),
    ]
