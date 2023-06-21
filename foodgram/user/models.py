from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.settings import BANNED_SYMBOLS


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        verbose_name='email',
        null=False,
        unique=True,
        max_length=254
    )
    password = models.CharField(
        verbose_name='Пароль',
        null=False,
        max_length=150,
        help_text='Пароль необходим!',
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
        unique=True,
        null=False,
        help_text='Юзернейм',
        validators=[
            RegexValidator(
                regex=BANNED_SYMBOLS,
                message='Имя пользователя должно состоять из букв и цифр',
                code='Invalid_username'
            ),
        ]
    )
    is_active = models.BooleanField(
        verbose_name='Активирован',
        null=False,
        default=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        null=False,
        max_length=150,
        help_text='Имя пользователя',
    )
    last_name = models.CharField(
        null=False,
        verbose_name='Фамилия',
        max_length=150,
        help_text='Фамилия пользователя',
    )
    username_field = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return f'Пользователь {self.email}'


User = FoodgramUser


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
        ordering = ('user', )

    def __str__(self):
        return f'{self.user} {self.following}'
