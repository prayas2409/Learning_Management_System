from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name']
        extra_kwargs = {'id': {'read_only': True}}

    def validate(self, data):
        data['course_name'] = data['course_name'].upper()
        return data