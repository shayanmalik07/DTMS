# permissions.py
from rest_framework import permissions
from .models import User


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        return (
            request.user and 
            request.user.is_authenticated and 
            user_role in [User.Role.SUPER_ADMIN, 'super_admin', 'SUPER_ADMIN']
        )


class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        allowed_roles = [
            User.Role.SUPERVISOR, 'supervisor', 'SUPERVISOR',
            User.Role.SUPER_ADMIN, 'super_admin', 'SUPER_ADMIN'
        ]
        return (
            request.user and 
            request.user.is_authenticated and 
            user_role in allowed_roles
        )


class IsOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        allowed_roles = [User.Role.OFFICER, 'officer', 'OFFICER']
        return (
            request.user and 
            request.user.is_authenticated and 
            user_role in allowed_roles
        )