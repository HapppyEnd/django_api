from rest_framework.permissions import BasePermission

class IsAdminOrIsSelf(BasePermission):
    """
    Разрешает доступ только администраторам или пользователю, который запрашивает свой собственный профиль.
    """

    def has_permission(self, request, view):
        # Проверяем, является ли пользователь администратором
        if request.user and request.user.is_staff:
            return True
        # Проверяем, совпадает ли ID текущего пользователя с ID в URL
        return request.user and request.user.is_authenticated
