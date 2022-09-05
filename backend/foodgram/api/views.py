from rest_framework import viewsets, permissions, views, status, pagination
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from .serializers import UserSerializer, RecipeSerializer, SubcriptionsSerializer
from .permissions import IsAdminOrAuthorOrReadOnly
from recipes.models import Subscribe, Recipe

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = pagination.PageNumberPagination
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrAuthorOrReadOnly, ]

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(following__user=user)
        serializer = SubcriptionsSerializer(subscriptions,
                                            many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubcriptionsSerializer(author)
        if request.method == 'POST':
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            follow = Subscribe.objects.filter(author=author, user=user)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response('rfrf', status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = pagination.PageNumberPagination
    serializer_class = RecipeSerializer
    permissions = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
