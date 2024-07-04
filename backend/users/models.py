from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from .validators import validate_username


class User(AbstractUser):
    """Класс модели пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    username = models.CharField(
        'Никнейм', unique=True, max_length=settings.USERNAME_LENGTH,
        validators=[validate_username])
    email = models.EmailField(
        'Почта', unique=True, max_length=settings.EMAIL_LENGTH)
    first_name = models.CharField('Имя', blank=True, null=True, max_length=50)
    last_name = models.CharField(
        'Фамилия', blank=True, null=True, max_length=50)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        default=None,
        verbose_name='Аватар',
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Класс модели подписки."""
    user = models.ForeignKey(
        User,
        related_name='subscriptions_received',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscriptions_sent',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['author']
        constraints = [
            UniqueConstraint(
                fields=[
                    'user',
                    'author'],
                name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
