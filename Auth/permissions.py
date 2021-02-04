from rest_framework import permissions


class isAdmin(permissions.BasePermission):
    message = {'response': 'You are not an admin. Access Denied!'}

    def has_permission(self, request, view):
        if request.user.role == 'Admin':
            return True
        return False


class isMentorOrAdmin(permissions.BasePermission):
    message = {'response': 'You are not an Admin or a Mentor. Access Denied!'}

    def has_permission(self, request, view):
        return request.user.role == 'Mentor' or request.user.role == 'Admin'
