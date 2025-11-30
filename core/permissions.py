# core/permissions.py
from rest_framework.permissions import BasePermission

class IsCEO(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", "") == "CEO"
        )


class IsSales(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", "") == "Sales"
        )


class IsOps(BasePermission):
    """
    Only allow access to users whose role = 'Ops'
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", "") == "Ops"
        )


class IsProQualAdmin(BasePermission):
    """
    Only allow access to users whose role = 'ProQualAdmin'
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", "") == "ProQualAdmin"
        )