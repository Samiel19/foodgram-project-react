# Generated by Django 3.2.16 on 2023-06-21 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20230621_0839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodgramuser',
            name='first_name',
            field=models.CharField(help_text='Имя пользователя', max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='foodgramuser',
            name='last_name',
            field=models.CharField(help_text='Фамилия пользователя', max_length=150, verbose_name='Фамилия'),
        ),
    ]