from rest_framework import serializers
from .models import Course, Mentor, StudentCourseMentor, Student, Education, Performance
import sys

sys.path.append('..')
from Auth.models import User


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'duration_weeks']
        extra_kwargs = {'id': {'read_only': True}, 'duration_weeks': {'required': True}}

    def validate(self, data):
        data['course_name'] = data['course_name'].upper()
        return data


class CourseMentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentor
        fields = ['mentor', 'course']
        extra_kwargs = {'mentor': {'read_only': True}}


class MentorSerializer(serializers.ModelSerializer):
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Mentor
        fields = ['id', 'mentor', 'course']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'mobile', 'role']


class StudentCourseMentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseMentor
        fields = ['student', 'course', 'mentor', 'create_by']
        extra_kwargs = {'course': {'required': True}, 'mentor': {'required': True}, 'create_by': {'read_only': True}}

    def validate(self, data):
        data['create_by'] = self.context['user']
        return data


class StudentCourseMentorReadSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    create_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = StudentCourseMentor
        fields = ['id', 'student_id', 'mentor_id', 'course_id', 'student', 'mentor', 'course', 'create_by',
                  'updated_by']


class StudentCourseMentorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseMentor
        fields = ['course', 'mentor', 'updated_by']
        extra_kwargs = {'course': {'required': True}, 'mentor': {'required': True}, 'updated_by': {'read_only': True}}

    def validate(self, data):
        data['updated_by'] = self.context['user']
        return data


class StudentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    mentor = serializers.StringRelatedField(read_only=True)
    mentor_id = serializers.IntegerField()
    course_id = serializers.IntegerField()

    class Meta:
        model = StudentCourseMentor
        fields = ['id', 'course_id', 'student_id', 'mentor_id', 'student', 'course', 'mentor']


class StudentBasicSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'student']


class StudentDetailsSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Education
        fields = "__all__"


class CourseMentorSerializerDetails(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = StudentCourseMentor
        fields = ['id', 'student_id', 'mentor_id', 'course_id', 'student', 'mentor', 'course']


class NewStudentsSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student', 'course_assigned']


class PerformanceSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    update_by = serializers.StringRelatedField(read_only=True)
    score = serializers.FloatField(max_value=10, min_value=1)
    review_date = serializers.DateField(required=True)

    class Meta:
        model = Performance
        fields = ['student_id', 'student',  'course_id', 'course', 'mentor_id', 'mentor', 'score', 'week_no',
                  'review_date', 'update_by']
        read_only_fields = ('student', 'week_no', 'mentor', 'course', 'update_by')

    def validate(self, data):
        data['update_by'] = self.context['user']
        return data