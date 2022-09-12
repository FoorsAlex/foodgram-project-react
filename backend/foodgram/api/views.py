from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, pagination, filters
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
import io
from django.db.models import F, Sum
from django.http import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .serializers import UserSerializer, RecipeSerializer, SubcriptionsSerializer, SubscribeRecipeSerializer, \
    IngredientSerializer
from .permissions import IsAuthenticatedOrReadOnly
from recipes.models import Recipe, Favorite, IngredientAmount, ShoppingCart, Ingredient
from users.models import Subscribe
from .paginations import PageNumberLimitPagination
from .filtersets import RecipeFilterSet
from .viewsets import RetrieveListViewSet

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
            permission_classes=[permissions.IsAuthenticated])
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
                                ' автора или пытаетесь подписаться на самого себя',
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
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        Story = []
        styles = getSampleStyleSheet()
        shopping_list = IngredientAmount.objects.filter(
            recipe__shopping_cart_recipe__user=request.user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(total_amount=Sum('amount'))
        for i in shopping_list:
            ptext = f'{i["name"]} ({i["measurement_unit"]}) - {i["total_amount"]}'
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
        doc.build(Story)
        buffer.seek(0)
        return FileResponse(buffer, filename='shopping_cart.pdf')


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('^name',)
