from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Tag, IngredientAmount, ShoppingCart
from users.models import Subscribe


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'in_favorite'
    )
    list_editable = ('name',)
    search_fields = ('name', 'author__username', 'tags__name')
    empty_value_display = '-пусто-'

    def in_favorite(self, obj):
        in_favorite = Favorite.objects.filter(favorite_recipe=obj)
        return in_favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = ('recipe__name',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'favorite_recipe',
        'user'
    )
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user'
    )
    search_fields = ('recipe__name', 'user__username')
    empty_value_display = '-пусто-'


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscribe, SubscribeAdmin)

