from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг',
        max_length=64,
        unique=True
    )
    color = models.CharField(
        verbose_name='Тэг',
        max_length=7,
        unique=True,
    )
    slug = models.CharField(
        verbose_name='Слаг',
        max_length=64,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингридиент',
        max_length=64,
    )
    amount = models.CharField(
        verbose_name='Количество',
        max_length=64,
    )
    units = models.CharField(
        verbose_name='Единицы измерения',
        max_length=64,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.units}'
    

class Recipy(models.Model):
    name = models.CharField(
        verbose_name='Название блюда',
        max_length = 64
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        through='recipy.AmountIngredient',
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
        max_length=500,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=0,
    )
    
    class Meta:
        default_related_name = 'recipies'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'


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
        verbose_name = 'Избранное'

    def __str__(self) -> str:
        return f'{self.user}: {self.recipy}'
    

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Читаемый автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follower'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='no_selfsubscribe'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipy,
        verbose_name='В каких блюдах',
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        to=Ingredient,
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
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='Это уже добавили!',
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredients}'