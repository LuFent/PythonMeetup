# Generated by Django 4.0.4 on 2022-08-05 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0009_alter_participant_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='level',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='telegram_bot.access', verbose_name='Уровень доступа'),
        ),
    ]
