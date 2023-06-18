import datetime
from api.mixins import AddDelViewMixin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import F, Q, QuerySet, Sum
from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework import viewsets, filters, pagination, status, generics
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, IsAdminUser, DjangoModelPermissions)

from recipy.models import Ingredient, Recipy, Tag, User, Favorites, Cart, IngredientAmount
from user.models import Follow
from .serializers import (
    TagSerializer,
    RecipySerializer,
    UserSerializer,
    FollowSerializer,
    IngredientSerializer,
    ShortRecipySerializer,
    FavoritesSerializer,
    CartSerializer,
    UserFollowSerializer
)
from .permissions import IsAuthorOrReadOnlyPermission, AdminOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import decorators
from djoser.views import UserViewSet as UV


METHODS = 'GET', 'POST', 'DELETE',


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]

    @decorators.action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowApiView(APIView):
    permission_classes = [IsAuthenticated, ]

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
    permission_classes = [IsAuthenticated, ]
    serializer_class = FollowSerializer
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = 6

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
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = 6
    add_serializer = ShortRecipySerializer

    def get_queryset(self):

        queryset = self.queryset

        author = self.request.query_params.get('author')
        tags = self.request.query_params.get('tags')
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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)


class FavoritesViewSet(APIView):
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
    

class CartViewSet(APIView):
    permission_classes = [IsAuthenticated, ]
    
    def post(self, request, recipy_id):
        user = request.user
        data = {
            'recipy': recipy_id,
            'user': user.id
        }
        serializer = CartSerializer(data=data,
                                         context={'request': request})
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
            units = ingredient.ingredients.units
            if name not in shopping_list:
                shopping_list[name] = {
                    'units': units,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
        user_shopping_list = ([
            f"{i + 1}. {item}: {value['amount']}"
            f" {value['units']}\n" for i, (item, value) in enumerate(shopping_list.items())
            ])
        today = datetime.date.today()
        user_shopping_list.append(f'\nCreated with Foodgram by Samiel19, {today.year}')
        response = HttpResponse(
            user_shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response