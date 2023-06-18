from api.views import (IngredientViewSet, RecipyViewSet,
                       TagViewSet, UserViewSet, FavoritesViewSet, CartViewSet, FollowListApiView, FollowApiView, DownloadShoppingCart
                       )
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.conf import settings

app_name = 'api'

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipyViewSet)

urlpatterns = [
    path('users/subscriptions/', FollowListApiView.as_view()),
    path('users/<int:following_id>/subscribe/', FollowApiView.as_view()),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('recipes/<int:favorite_id>/favorite/', FavoritesViewSet.as_view()),
    path('recipes/<int:recipy_id>/shopping_cart/', CartViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)