from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (CartView, DownloadShoppingCart, FavoritesView,
                       FollowApiView, FollowListApiView, IngredientView,
                       RecipeViewSet, TagViewSet,)

app_name = 'api'

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientView)
router.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('users/subscriptions/', FollowListApiView.as_view()),
    path('users/<int:following_id>/subscribe/', FollowApiView.as_view()),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('recipes/<int:favorite_id>/favorite/', FavoritesView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', CartView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
