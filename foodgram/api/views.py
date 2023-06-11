from rest_framework import viewsets, filters, pagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, IsAdminUser)

from recipy.models import Follow, Ingredient, Recipy, Tag, User
from .serializers import (
    TagSerializer,
    RecipySerializer,
    UserSerializer,
    FollowSerializer,
    IngredientSerializer
)
from .permissions import IsAuthorOrReadOnlyPermission


class RecipyViewSet(viewsets.ModelViewSet):
    queryset = Recipy.objects.all()
    serializer_class = RecipySerializer
    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUser,)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminUser,)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username', 'following__username')

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
