from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, default=None, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']


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
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Владелец списка',
                             related_name='owner_cart',
                             )


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




