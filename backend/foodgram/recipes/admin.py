from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Recipe, Tag, Ingredient

User = get_user_model()


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'image',
        'cooking_time',
        'name'
    )
    list_editable = ('name', 'text')
    search_fields = ('text', 'name')
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
