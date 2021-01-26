from django.contrib import admin
from .models import Course, Mentors, Student, Education, Performance
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Performance)
admin.site.register(Mentors)
admin.site.register(Education)
