from rest_framework import serializers
from .models import Course


class AddCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name']

    def validate(self, data):
        data['course_name'] = data['course_name'].upper()
        return data
