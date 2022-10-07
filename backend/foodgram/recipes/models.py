from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, default=None, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [UniqueConstraint(fields=['name', 'slug'],
                                        name='unique_booking')]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        constraints = [UniqueConstraint(fields=['name', 'measurement_unit'],
                                        name='unique_booking')]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               related_name='author',
                               on_delete=models.CASCADE,
                               verbose_name='Автор рецепта'
                               )
    image = models.ImageField(upload_to='recipe')
    name = models.CharField(max_length=200)
    text = models.TextField()
    tags = models.ManyToManyField(Tag, related_name='tags')
    pub_date = models.DateTimeField(auto_now_add=True)
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   related_name='ingredient',
                                   verbose_name='Ингредиент в рецепте',
                                   on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe,
                               related_name='ingredientsamount',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE)
    amount = models.IntegerField()

    class Meta:
        constraints = [UniqueConstraint(fields=['recipe', 'ingredient'],
                                        name='unique_booking')]
        verbose_name = 'Ингредиент рецпта'
        verbose_name_plural = 'Ингредиенты рецепта'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name=('Рецепт '
                                             'в списке покупок'),
                               related_name='shopping_cart_recipe')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Владелец списка',
                             related_name='owner_cart',
                             )

    class Meta:
        constraints = [UniqueConstraint(fields=['recipe', 'user'],
                                        name='unique_booking')]
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списках покупок'


class Favorite(models.Model):
    favorite_recipe = models.ForeignKey(Recipe,
                                        related_name='favorite_recipe',
                                        verbose_name='Избранный рецепт',
                                        on_delete=models.CASCADE
                                        )
    user = models.ForeignKey(User,
                             related_name='user_added_favorite',
                             verbose_name='Пользователь,'
                                          ' добавивший рецепт в избранное',
                             on_delete=models.CASCADE)

    class Meta:
        constraints = [UniqueConstraint(fields=['favorite_recipe', 'user'],
                                        name='unique_booking')]
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
