from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RecipeViewSet, IngredientViewSet
from django.urls import path, include

router = DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
    ]
