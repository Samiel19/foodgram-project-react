# Generated by Django 3.2.16 on 2023-06-27 06:13

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0004_auto_20230626_0650'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='recipe',
            managers=[
                ('recipes', django.db.models.manager.Manager()),
            ],
        ),
    ]
