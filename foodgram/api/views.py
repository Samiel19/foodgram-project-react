import datetime

from django.shortcuts import get_object_or_404
from django.http import FileResponse

from rest_framework import generics, pagination, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import AdminOrReadOnly, IsAuthorAdminOrReadOnlyPermission
from .serializers import (CartSerializer, FavoritesSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipySerializer, TagSerializer,
                          UserFollowSerializer)
from recipy.models import (Cart, Favorites, Ingredient, IngredientAmount,
                           Recipy, Tag, User)
from user.models import Follow


class FollowApiView(APIView):
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)

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
        user = request.user
        following = get_object_or_404(User, id=following_id)
        Follow.objects.filter(user=user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowListApiView(generics.ListAPIView):
    serializer_class = FollowSerializer
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = 6
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class RecipyViewSet(viewsets.ModelViewSet):
    queryset = Recipy.objects.select_related('author')
    serializer_class = RecipySerializer
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = 6

    def get_queryset(self):
        queryset = self.queryset
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        in_cart = self.request.query_params.get('is_in_shopping_cart')
        is_favorite = self.request.query_params.get('is_favorited')
        if is_favorite:
            queryset = queryset.filter(favorite_recipy__user=self.request.user)
        if in_cart:
            queryset = queryset.filter(in_cart__user=self.request.user)
        if author:
            queryset = queryset.filter(author=author)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        else:
            queryset = queryset
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class FavoritesView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, favorite_id):
        user = request.user
        data = {
            'recipy': favorite_id,
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
        user = request.user
        recipy = get_object_or_404(Recipy, id=favorite_id)
        Favorites.objects.filter(user=user, recipy=recipy).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, recipy_id):
        user = request.user
        data = {
            'recipy': recipy_id,
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

    def delete(self, request, recipy_id):
        user = request.user
        recipy = get_object_or_404(Recipy, id=recipy_id)
        Cart.objects.filter(user=user, recipy=recipy).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        shopping_list = {}
        filename = f'{request.user.username}_shopping_list.txt'
        ingredients = IngredientAmount.objects.filter(
            recipy__in_cart__user=request.user
        )
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
        response = FileResponse(
            user_shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
