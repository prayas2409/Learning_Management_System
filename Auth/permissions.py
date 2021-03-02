from rest_framework import permissions
import enum

from Auth.models import Roles

class isAdmin(permissions.BasePermission):
    message = {'response': 'You are not an admin. Access Denied!'}

    def has_permission(self, request, view):
        """ This function is used for Admin permission"""
        return request.META['user'].role == Roles.objects.get(role='admin') or request.META['user'].is_superuser


class isMentorOrAdmin(permissions.BasePermission):
    message = {'response': 'You are not an Admin or a Mentor. Access Denied!'}

    def has_permission(self, request, view):
        """ This function is used for Admin or Mentor permission"""
        return request.META['user'].role == Roles.objects.get(role='mentor') or request.META['user'].role == Roles.objects.get(role='admin')


class OnlyStudent(permissions.BasePermission):
    message = {'response': 'Only student can access'}

    def has_permission(self, request, view):
        """ This function is used for Student permission"""
        return request.META['user'].role == Roles.objects.get(role='student')
