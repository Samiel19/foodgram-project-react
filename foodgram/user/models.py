from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    email = models.EmailField('email', null=False, unique=True)
    password = models.CharField(
        verbose_name=('Пароль'),
        max_length=150,
        help_text='Пароль необходим!',
    )
    username_field = 'email'
    required_fields = ['username', 'first_name', 'last_name']
    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )

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
