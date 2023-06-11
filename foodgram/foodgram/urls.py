from api.views import (IngredientViewSet, RecipyViewSet,
                       TagViewSet, UserViewSet)
from django.urls import include, path
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from rest_framework import routers


router = routers.DefaultRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipyViewSet, 'recipes')
router.register('users', UserViewSet, 'users')

urlpatterns = (
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
)