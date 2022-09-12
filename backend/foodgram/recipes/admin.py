from django.contrib import admin

from .models import Recipe, Tag, Ingredient, Favorite


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'in_favorite'
    )
    list_editable = ('name',)
    list_filter = ('name', 'tags', 'author')
    empty_value_display = '-пусто-'

    def in_favorite(self, obj):
        in_favorite = Favorite.objects.filter(favorite_recipe=obj)
        return in_favorite.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
