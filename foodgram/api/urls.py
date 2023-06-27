from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (CartViewSet, FavoritesViewSet,
                       FollowViewSet, IngredientViewSet,
                       RecipeViewSet, TagViewSet,)

app_name = 'api'

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('users/subscriptions/', FollowViewSet.as_view(
        {'get': 'list'}
    )),
    path('users/<int:following_id>/subscribe/', FollowViewSet.as_view(
        {'get': 'list'}
    )),
    path('recipes/download_shopping_cart/', CartViewSet.as_view(
        {'get': 'download_shopping_cart'}
    )),
    path('recipes/<int:favorite_id>/favorite/', FavoritesViewSet.as_view(
        {'get': 'list'}
    )),
    path('recipes/<int:recipe_id>/shopping_cart/', CartViewSet.as_view(
        {'get': 'list'}
    )),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
