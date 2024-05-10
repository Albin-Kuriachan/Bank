
from rest_framework import permissions

class IsNotAdminOrStaff(permissions.BasePermission):
    """
    Custom permission to allow access only to non-admin and non-staff users.
    """

    def has_permission(self, request, view):
        return request.user and not (request.user.is_staff or request.user.is_superuser)



class IsAdminOrStaff(permissions.BasePermission):
    """
    Custom permission to allow access to superusers and staff members.
    """

    def has_permission(self, request, view):
        return request.user and ( request.user.is_superuser)
