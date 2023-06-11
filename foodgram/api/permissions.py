from rest_framework import permissions
from django.db.models import Model
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.routers import APIRootView


class BanPermission(BasePermission):
    def has_permission(
        self,
        request: WSGIRequest,
        view: APIRootView
    ):
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )



class IsAuthorOrReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user or obj.author.is_staff:
            return True
        return request.method in permissions.SAFE_METHODS

class OwnerUserOrReadOnly(BanPermission):
    def has_object_permission(
        self,
        request: WSGIRequest,
        view: APIRootView,
        obj: Model
    ):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )