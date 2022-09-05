from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, default=None, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)


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
    cooking_time = models.IntegerField()
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)


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


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name=('Рецепт '
                                             'в списке покупок'),
                               related_name='shopping_cart_recipe')
    user = models.ForeignKey(Recipe,
                             on_delete=models.CASCADE,
                             verbose_name='Владелец списка',
                             related_name='owner_cart')


class Favorite(models.Model):
    favorite_recipe = models.ForeignKey(Recipe,
                                        related_name='favorite_recipe',
                                        verbose_name='Избранный рецепт',
                                        on_delete=models.CASCADE
                                        )
    user = models.ForeignKey(User,
                             related_name='user_added_favorite',
                             verbose_name='Автор рецепта',
                             on_delete=models.CASCADE)


class Subscribe(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               related_name='following',
                               on_delete=models.CASCADE)