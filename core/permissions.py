# core/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

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


class IsHR(BasePermission):
    """
    Only allow access to users whose role = 'HR'
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", "") == "HR"
        )


class IsFinance(BasePermission):
    """
    Only allow access to users whose role = 'Finance'
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", "") == "Finance"
        )


class IsAdminOrSales(BasePermission):
    """
    Custom permission class that allows:
    - SAFE_METHODS (GET, HEAD, OPTIONS) for all authenticated users
    - Unsafe methods (POST, PUT, PATCH, DELETE) only for users with roles 'CEO', 'Sales', 'ProQualAdmin', or 'Finance'
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow SAFE_METHODS for all authenticated users
        if request.method in SAFE_METHODS:
            return True
        
        # Restrict unsafe methods to CEO, Sales, ProQualAdmin, or Finance
        user_role = getattr(request.user, "role", "")
        return user_role in ("CEO", "Sales", "ProQualAdmin", "Finance")