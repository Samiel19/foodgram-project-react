from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from foodgram.settings import RECIPE_MODEL_MAX_LEN, HEX_LEN


User = get_user_model()


class RecipyQuerySet(models.QuerySet):
    def recipe_filter(
            self,
            user,
            is_favorite,
            in_cart,
            author,
            tags
    ):
        if is_favorite:
            return self.filter(favorite_recipe__user=user)
        if in_cart:
            return self.filter(in_cart__user=user)
        if author:
            return self.filter(author=author)
        if tags:
            return self.filter(tags__slug__in=tags).distinct()
        else:
            return self


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг',
        max_length=RECIPE_MODEL_MAX_LEN,
        unique=True,
        null=False,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        default='#0000FF',
        max_length=HEX_LEN,
        unique=True,
        validators=[MinLengthValidator(7)]
    )
    slug = models.CharField(
        verbose_name='Слаг',
        max_length=RECIPE_MODEL_MAX_LEN,
        unique=True,
        null=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.color}'

    def clean(self):
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        return super().clean()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингридиент',
        max_length=RECIPE_MODEL_MAX_LEN,
        null=False
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=RECIPE_MODEL_MAX_LEN,
        null=False
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        ]

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=RECIPE_MODEL_MAX_LEN,
        null=False,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='IngredientAmount',
    )
    created_at = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    image = models.ImageField(
        verbose_name='Внешний вид блюда',
        upload_to='recipe_images/',
    )
    text = models.TextField(
        verbose_name='Описание блюда',
        null=False
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, 'Меньше минуты - не рецепт!')
        ]
    )
    recipes = RecipyQuerySet.as_manager()

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at', )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких блюдах',
        related_name='ingredients_in_recipe',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=0,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='Это уже добавили!',
            ),
        ]

    def __str__(self):
        return f'{self.amount} в {self.ingredients}'


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в корзине',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Это список пользователя',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        default_related_name = 'in_cart'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_cart'),
        ]
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        ordering = ('recipe', )

    def __str__(self):
        return f'{self.user}: {self.recipe}'


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранные рецепты',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        default_related_name = 'favorite_recipe'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite'),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.user}: {self.recipe}'
