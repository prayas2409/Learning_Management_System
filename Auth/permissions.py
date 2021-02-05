from rest_framework import permissions
import enum


class Role(enum.Enum):

    ADMIN = 'Admin'
    MENTOR = 'Mentor'
    STUDENT = 'Engineer'


class isAdmin(permissions.BasePermission):
    message = {'response': 'You are not an admin. Access Denied!'}

    def has_permission(self, request, view):
        if request.user.role == Role.ADMIN.value:
            return True
        return False


class isMentorOrAdmin(permissions.BasePermission):
    message = {'response': 'You are not an Admin or a Mentor. Access Denied!'}

    def has_permission(self, request, view):
        return request.user.role == Role.MENTOR.value or request.user.role == Role.STUDENT.value


class OnlyStudent(permissions.BasePermission):
    message = {'response': 'Only student can access'}

    def has_permission(self, request, view):
        print(Role.STUDENT)
        return request.user.role == Role.STUDENT.value
