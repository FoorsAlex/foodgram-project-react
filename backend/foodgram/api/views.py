from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscribe
from .filtersets import RecipeFilterSet, IngredientSearchFilter
from .paginations import PageNumberLimitPagination
from .permissions import IsAuthenticatedOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubcriptionsSerializer, SubscribeRecipeSerializer,
                          TagSerializer, UserSerializer)
from .viewsets import RetrieveListViewSet
from .utils import get_shopping_cart_pdf

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberLimitPagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    @action(methods=['get'],
            detail=False)
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubcriptionsSerializer(page,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated],
            )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'DELETE':
            follow = Subscribe.objects.filter(author=author, user=user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            already_subscribe = Subscribe.objects.filter(author=author,
                                                         user=user).exists()
            if already_subscribe or user == author:
                return Response('Вы уже подписаны на этого'
                                ' автора или пытаетесь'
                                ' подписаться на самого себя',
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubcriptionsSerializer(author,
                                                context={'request': request})
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberLimitPagination
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'],
            detail=True)
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        favorite = Favorite.objects.filter(user=user,
                                           favorite_recipe=recipe)
        if request.method == 'DELETE':
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            serializer = SubscribeRecipeSerializer(recipe)
            if favorite.exists():
                return Response('Вы уже добавили'
                                ' этот рецепт в избранное',
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user,
                                    favorite_recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post', 'delete'],
            detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        in_shopping_cart = ShoppingCart.objects.filter(user=user,
                                                       recipe=recipe)
        if request.method == 'DELETE':
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            serializer = SubscribeRecipeSerializer(recipe)
            if in_shopping_cart.exists():
                return Response('Вы уже добавили'
                                ' этот рецепт в список покупок',
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user,
                                        recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get'],
            detail=False, )
    def download_shopping_cart(self, request):
        pdf = get_shopping_cart_pdf(request)
        return FileResponse(pdf, filename='shopping_cart.pdf')


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class TagViewSet(RetrieveListViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
