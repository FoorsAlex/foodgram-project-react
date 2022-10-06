from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(default=False)

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Subscribe.objects.filter(
            user=request_user, author=obj.id
        ).exists()
        return queryset

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ('__all__',)


class SubcriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, obj):
        return obj.author.count()

    def get_recipes(self, obj):
        recipes = SubscribeRecipeSerializer(instance=obj.author,
                                            many=True).data
        return recipes

    def to_representation(self, instance):
        recipes = SubscribeRecipeSerializer(instance=instance.author,
                                            many=True).data
        query_params = self.context.get('request').query_params
        data = super(SubcriptionsSerializer, self).to_representation(instance)
        if 'recipes_limit' in query_params:
            recipes_limit = int(query_params['recipes_limit'])
            data['recipes'] = recipes[:recipes_limit]
        return data

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['recipes', 'recipes_count']
        read_only_fields = ('__all__',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name',
                                 read_only=True)
    measurement_unit = serializers.CharField(source=
                                             'ingredient.measurement_unit',
                                             read_only=True)

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False, read_only=True)
    ingredients = IngredientAmountSerializer(many=True,
                                             source='ingredientsamount')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте хотябы один ингредиент')
        ingredient_list = []
        for ingredient_item in value:
            if ingredient_item in ingredient_list:
                raise ValidationError('Ингредиенты должны быть уникальны')
            if ingredient_item['amount'] <= 0:
                raise ValidationError('Количество не '
                                      'может быть меньше или равно 0')
            ingredient_list.append(ingredient_item)
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise ValidationError('Время приготовления'
                                  ' не должно быть меньше 1')
        return value

    def get_is_favorited(self, obj):
        user = self.context.get('request').user.id
        return Favorite.objects.filter(user__id=user,
                                       favorite_recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user.id
        return ShoppingCart.objects.filter(user__id=user,
                                           recipe=obj).exists()

    def create_ingredient(self, recipe, ingredients_amount_dict):
        IngredientAmount.objects.bulk_create([
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient_amount_item['ingredient']['id'],
                amount=ingredient_amount_item['amount']
            ) for ingredient_amount_item in ingredients_amount_dict
        ])

    def create(self, validated_data):
        ingredients_amount_dict = validated_data.pop('ingredientsamount')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredient(recipe, ingredients_amount_dict)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientAmount.objects.filter(recipe=instance, ).delete()
        self.create_ingredient(instance,
                               validated_data.pop('ingredientsamount'))
        instance.tags.set(validated_data.pop('tags'))
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags,
                                               many=True).data
        return representation

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )
