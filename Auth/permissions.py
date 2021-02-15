from rest_framework import permissions
import enum


class Role(enum.Enum):

    ADMIN = 'Admin'
    MENTOR = 'Mentor'
    STUDENT = 'Engineer'


class isAdmin(permissions.BasePermission):
    message = {'response': 'You are not an admin. Access Denied!'}

    def has_permission(self, request, view):
        return request.META['user'].role == Role.ADMIN.value or request.META['user'].is_superuser


class isMentorOrAdmin(permissions.BasePermission):
    message = {'response': 'You are not an Admin or a Mentor. Access Denied!'}

    def has_permission(self, request, view):
        return request.META['user'].role == Role.MENTOR.value or request.META['user'].role == Role.ADMIN.value


class OnlyStudent(permissions.BasePermission):
    message = {'response': 'Only student can access'}

    def has_permission(self, request, view):
        return request.META['user'].role == Role.STUDENT.value
