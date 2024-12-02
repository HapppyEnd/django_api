from rest_framework.permissions import BasePermission


class IsAdminOrIsSelf(BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        return request.user and request.user.is_authenticated
