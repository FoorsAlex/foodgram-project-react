from rest_framework import viewsets, permissions, views, status, pagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .serializers import UserSerializer, RecipeSerializer, SubcriptionsSerializer, SubscribeRecipeSerializer
from .permissions import IsAuthenticatedOrReadOnly
from recipes.models import Recipe, Favorite
from users.models import Subscribe

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = pagination.PageNumberPagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    @action(methods=['get'],
            detail=False,
            pagination_class=pagination.PageNumberPagination)
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        serializer = SubcriptionsSerializer(subscriptions,
                                            many=True,
                                            context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    pagination_class = pagination.PageNumberPagination
    serializer_class = RecipeSerializer
    permissions = [IsAuthenticatedOrReadOnly]

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
