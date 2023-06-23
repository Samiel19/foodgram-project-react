# Generated by Django 3.2.16 on 2023-06-23 06:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'default_related_name': 'in_cart', 'ordering': ('recipe',), 'verbose_name': 'Рецепт в корзине', 'verbose_name_plural': 'Рецепты в корзине'},
        ),
        migrations.AlterModelOptions(
            name='favorites',
            options={'default_related_name': 'favorite_recipe', 'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_cart', to=settings.AUTH_USER_MODEL, verbose_name='Это список пользователя'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipe', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]