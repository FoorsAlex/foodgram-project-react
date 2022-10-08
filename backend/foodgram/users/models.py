from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class MyUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, )
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=150, )
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.is_superuser or self.is_staff

    class Meta:
        constraints = [UniqueConstraint(fields=['username', 'email'],
                                        name='unique_username_email')]
        ordering = ['username']
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    user = models.ForeignKey(MyUser,
                             related_name='follower',
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(MyUser,
                               verbose_name='Автор',
                               related_name='following',
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'author'],
                                        name='unique_booking')]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
