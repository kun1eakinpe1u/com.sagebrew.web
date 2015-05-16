from rest_framework import permissions

from plebs.neo_models import Pleb


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (obj.owned_by.all()[0].username == request.user.username or
                request.user.is_staff):
            return True
        else:
            return False


class IsSelfOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.username == request.user.username


class IsSelf(permissions.BasePermission):
    """
    @DEPRECATED
    This is deprecated due to the implementation of the /me endpoint.
    Any endpoints that should only be accessible by the currently logged
    in user should be placed on this endpoint.
    See WA-1250 https://sagebrew.atlassian.net/browse/WA-1250
    """
    def has_object_permission(self, request, view, obj):
        return obj.username == request.user.username


class IsUserOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user or request.user.is_staff:
            return True
        else:
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


class IsOwnerOrEditorOrAccountant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        pleb = Pleb.get(username=request.user.username)
        if (obj.owned_by.all()[0].username == request.user.username or
                    pleb in obj.editors.all() or
                    pleb in obj.accountants.all()):
            return True
        else:
            return False
