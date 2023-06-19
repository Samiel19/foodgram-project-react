# Generated by Django 3.2.16 on 2023-06-18 08:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipy',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта'),
        ),
        migrations.AddField(
            model_name='recipy',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipy.IngredientAmount', to='recipy.Ingredient', verbose_name='Ингридиенты'),
        ),
        migrations.AddField(
            model_name='recipy',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipy.Tag', verbose_name='Тег'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipy', to='recipy.ingredient', verbose_name='Связанные ингредиенты'),
        ),
        migrations.AddField(
            model_name='ingredientamount',
            name='recipy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_in_recipy', to='recipy.recipy', verbose_name='В каких блюдах'),
        ),
        migrations.AddField(
            model_name='favorites',
            name='recipy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipy', to='recipy.recipy', verbose_name='Избранные рецепты'),
        ),
        migrations.AddField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='cart',
            name='recipy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_cart', to='recipy.recipy', verbose_name='Рецепты в корзине'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL, verbose_name='Это список пользователя'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipy', 'ingredients'), name='Это уже добавили!'),
        ),
        migrations.AddConstraint(
            model_name='favorites',
            constraint=models.UniqueConstraint(fields=('user', 'recipy'), name='unique_favorite'),
        ),
        migrations.AddConstraint(
            model_name='cart',
            constraint=models.UniqueConstraint(fields=('user', 'recipy'), name='unique_cart'),
        ),
    ]