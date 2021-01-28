from rest_framework import permissions


class isAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 'Admin':
            return True
        return False
