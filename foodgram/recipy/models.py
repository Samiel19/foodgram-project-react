from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг',
        max_length=64,
        unique=True,
        null=False
    )
    color = models.CharField(
        verbose_name='Цвет',
        default='#0000FF',
        max_length=7,
        unique=True,
        validators=[MinLengthValidator(7)]
    )
    slug = models.CharField(
        verbose_name='Слаг',
        max_length=64,
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
        max_length=64,
        null=False
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=64,
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

    def clean(self):
        self.name = self.name.strip().lower()
        self.measurement_unit = self.measurement_unit.strip().lower()
        return super().clean()


class Recipy(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=64,
        null=False
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингридиенты',
        through='IngredientAmount',
    )
    pub_date = models.DateTimeField(
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
        max_length=1000,
        null=False
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=0,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


class IngredientAmount(models.Model):
    recipy = models.ForeignKey(
        Recipy,
        verbose_name='В каких блюдах',
        related_name='ingredients_in_recipy',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipy',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=0,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipy', )
        constraints = [
            models.UniqueConstraint(
                fields=('recipy', 'ingredients', ),
                name='Это уже добавили!',
            ),
        ]

    def __str__(self):
        return f'{self.amount} в {self.ingredients}'


class Cart(models.Model):
    recipy = models.ForeignKey(
        Recipy,
        verbose_name='Рецепты в корзине',
        related_name='in_cart',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Это список пользователя',
        related_name='cart',
        on_delete=models.CASCADE,
    )
    add_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipy'],
                                    name='unique_cart'),
        ]
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        ordering = ('recipy', )

    def __str__(self):
        return f'{self.user}: {self.recipy}'


class Favorites(models.Model):
    recipy = models.ForeignKey(
        Recipy,
        verbose_name='Избранные рецепты',
        on_delete=models.CASCADE,
        related_name='favorite_recipy',
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipy'],
                                    name='unique_favorite'),
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.user}: {self.recipy}'
