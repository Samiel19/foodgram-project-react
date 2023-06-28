from django.shortcuts import get_object_or_404

from rest_framework import pagination, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.permissions import IsAuthorAdminOrReadOnlyPermission
from .serializers import UserFollowSerializer
from api.recipes.serializers import FollowSerializer
from recipe.models import User
from user.models import Follow

from foodgram.settings import RECIPE_ON_PAGE


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = RECIPE_ON_PAGE
    permission_classes = (IsAuthorAdminOrReadOnlyPermission,)

    def get_queryset(self):
        return User.objects.prefetch_related('follower').filter(
            following__user=self.request.user
        )

    @action(detail=True, methods=['post'])
    def follow(self, request, following_id):
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

    @action(detail=True, methods=['delete'])
    def unfollow(self, request, following_id):
        following = get_object_or_404(User, id=following_id)
        get_object_or_404(
            Follow, user=request.user, following=following
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
