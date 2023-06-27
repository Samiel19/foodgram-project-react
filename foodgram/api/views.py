import datetime

from django.shortcuts import get_object_or_404
from django.http import FileResponse

from rest_framework import pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import AdminOrReadOnly, IsAuthorAdminOrReadOnlyPermission
from .serializers import (CartSerializer, FavoritesSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          UserFollowSerializer)
from recipe.models import (Cart, Favorites, Ingredient, IngredientAmount,
                           Recipe, Tag, User)
from user.models import Follow

from foodgram.settings import RECIPE_ON_PAGE


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = RECIPE_ON_PAGE
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        return User.objects.prefetch_related('follower').filter(
            following__user=self.request.user
        )

    def post(self, request, following_id):
        user = request.user
        data = {
            'following': following_id,
            'user': user.id
        }
        serializer = UserFollowSerializer(data=data,
                                          context={'request': request})
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, following_id):
        following = get_object_or_404(User, id=following_id)
        get_object_or_404(
            Follow, user=request.user, following=following
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.recipes.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = RECIPE_ON_PAGE

    def get_queryset(self):
        return Recipe.recipes.recipe_filter(
            user=self.request.user,
            is_favorite=self.request.query_params.get('is_favorited'),
            in_cart=self.request.query_params.get('is_in_shopping_cart'),
            author=self.request.query_params.get('author'),
            tags=self.request.query_params.getlist('tags'),
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class FavoritesViewSet(viewsets.ModelViewSet):
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = RECIPE_ON_PAGE
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)

    def post(self, request, favorite_id):
        user = request.user
        data = {
            'recipe': favorite_id,
            'user': user.id
        }
        serializer = FavoritesSerializer(data=data,
                                         context={'request': request})
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, favorite_id):
        recipe = get_object_or_404(Recipe, id=favorite_id)
        get_object_or_404(
            Favorites, user=request.user, recipe=recipe
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = [IsAuthenticated, ]
    pagination_class.page_size = RECIPE_ON_PAGE

    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__in_cart__user=self.request.user
        )
        shopping_list = {}
        filename = f'{request.user.username}_shopping_list.txt'
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredients.name
            measurement_unit = ingredient.ingredients.measurement_unit
            if name not in shopping_list:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        user_shopping_list = ([
            f"{i + 1}. {item}: {value['amount']}"
            f" {value['measurement_unit']}\n" for i, (
                item, value
            ) in enumerate(
                shopping_list.items()
            )
        ])
        today = datetime.date.today()
        user_shopping_list.append(
            f'\nFoodgram by Samiel19, {today.strftime("%b-%d-%Y")}'
        )
        print(user_shopping_list)
        response = FileResponse(
            user_shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def post(self, request, recipe_id):
        user = request.user
        data = {
            'recipe': recipe_id,
            'user': user.id
        }
        serializer = CartSerializer(
            data=data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        get_object_or_404(
            Cart, user=request.user, recipe=recipe
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
