from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.recipes.views import RecipeViewSet, TagViewSet, IngredientViewSet
from api.users.views import UserViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('users/subscriptions/', UserViewSet.as_view(
        {'get': 'list'}
    )),
    path('users/<int:following_id>/subscribe/', UserViewSet.as_view(
        {'post': 'follow',
         'delete': 'unfollow'}
    )),
    path('recipes/download_shopping_cart/', RecipeViewSet.as_view(
        {'get': 'download_shopping_cart'}
    )),
    path('recipes/<int:favorite_id>/favorite/', RecipeViewSet.as_view(
        {'post': 'add_favorite',
         'delete': 'del_favorite'}
    )),
    path('recipes/<int:recipe_id>/shopping_cart/', RecipeViewSet.as_view(
        {'post': 'add_cart',
         'delete': 'del_cart'}
    )),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
