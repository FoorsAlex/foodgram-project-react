from django.db.models import Q
from django_filters import FilterSet, filters

from recipes.models import Recipe


class RecipeFilterSet(FilterSet):
    is_favorited = filters.CharFilter(method='favorite_filter')
    is_in_shopping_cart = filters.CharFilter(method='cart_filter')
    author = filters.CharFilter(method='author_filter')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def author_filter(self, queryset, name, value):
        try:
            int(value)
        except ValueError:
            return queryset
        return queryset.filter(author__id=value)

    def cart_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(shopping_cart_recipe__user=self.request.user)
        if value == '0':
            return queryset.filter(~Q(shopping_cart_recipe__user=self.request.user))
        return queryset

    def favorite_filter(self, queryset, name, value):
        if value:
            if value == '1':
                return queryset.filter(favorite_recipe__user=self.request.user)
            if value == '0':
                return queryset.filter(~Q(favorite_recipe__user=self.request.user))
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags']
