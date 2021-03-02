from rest_framework import serializers
from .models import Course, Mentor, StudentCourseMentor, Student, Education, Performance
import sys
import re
from .utils import Pattern

sys.path.append('..')
from Auth.models import User


class CourseSerializer(serializers.ModelSerializer):
    """
        This serializer is used to add new course, to get all courses, to delete any course and to update any course
    """
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'cid', 'duration_weeks', 'description', 'course_price']
        extra_kwargs = {'id': {'read_only': True}, 'duration_weeks': {'required': True}, 'cid': {'read_only': True}}

    def validate(self, data):
        data['course_name'] = data['course_name'].upper()
        return data

class CourseMentorSerializer(serializers.ModelSerializer):
    """
        This serializer is used to mape any mentor with any course
    """
    class Meta:
        model = Mentor
        fields = ['mid', 'mentor', 'course']
        extra_kwargs = {'mid': {'read_only': True}, 'mentor': {'read_only': True}}

class UserSerializer(serializers.ModelSerializer):
    """
        This serializer is used to get email, mobile of a user
    """
    class Meta:
        model = User
        fields = ['email', 'mobile']

class StudentCourseMentorSerializer(serializers.ModelSerializer):
    """
        This serializer is used to assign course and mentor to a student
    """
    class Meta:
        model = StudentCourseMentor
        fields = ['student', 'course', 'mentor', 'create_by']
        extra_kwargs = {'course': {'required': True}, 'mentor': {'required': True}, 'create_by': {'read_only': True}}

    def validate(self, data):
        data['create_by'] = self.context['user']
        return data


class StudentCourseMentorReadSerializer(serializers.ModelSerializer):
    """
        This serializer is used to fetch course and mentor details of a student
    """
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
    """
        This serializer is used to update course and mentor details of a student
    """
    class Meta:
        model = StudentCourseMentor
        fields = ['course', 'mentor', 'updated_by']
        extra_kwargs = {'course': {'required': False}, 'mentor': {'required': False}, 'updated_by': {'read_only': True}}

    def validate(self, data):
        data['updated_by'] = self.context['user']
        return data


class StudentSerializer(serializers.ModelSerializer):
    """
        This serializer is used to get all student basic details from student model
    """
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student', 'student_id', 'sid', 'alt_number', 'relation_with_alt_number_holder', 'current_location',
                  'current_address', 'git_link', 'year_of_experience']

class StudentBasicSerializer(serializers.ModelSerializer):
    """
        This serializer is used to get student id and name of a student
    """
    student = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'student']


class StudentDetailsSerializer(serializers.ModelSerializer):
    """
        This serializer is used to update student basic details
    """
    student = serializers.StringRelatedField(read_only=True)
    alt_number = serializers.RegexField("^[7-9]{1}[0-9]{9}$")
    relation_with_alt_number_holder = serializers.CharField(read_only=True, max_length=10)
    current_location = serializers.CharField(min_length=3, max_length=30, required=True)
    current_address = serializers.CharField(min_length=5, required=True)
    git_link = serializers.CharField(required=True, min_length=10)
    year_of_experience = serializers.IntegerField(required=True)

    class Meta:
        model = Student
        fields = ['id', 'student', 'alt_number', 'relation_with_alt_number_holder', 'current_location',
                  'current_address', 'git_link', 'year_of_experience']

    def validate(self, data):
        if not re.fullmatch(Pattern.GIT_PATTERN.value, data['git_link']):
            raise serializers.ValidationError('Invalid git link')
        if not re.fullmatch(Pattern.MOBILE_PATTERN.value, data['alt_number']):
            raise serializers.ValidationError('Invalid Mobile number format')
        return data


class EducationSerializer(serializers.ModelSerializer):
    """
        This serializer is used to get and post educational details of a student
    """
    student = serializers.StringRelatedField(read_only=True)
    institute = serializers.CharField(required=True)
    stream = serializers.CharField(required=True)
    percentage = serializers.FloatField(required=True)
    from_date = serializers.DateField(required=True)
    till = serializers.DateField(required=True)

    class Meta:
        model = Education
        fields = ['id', 'student_id', 'student', 'institute', 'degree', 'stream', 'percentage', 'from_date', 'till']

    def validate(self, data):
        data['student_id'] = self.context['student']  # storing logged in student id and returning with data
        return data


class EducationUpdateSerializer(serializers.ModelSerializer):
    """
        This serializer is used to update educational details of a student
    """
    institute = serializers.CharField(required=True)
    stream = serializers.CharField(required=True)
    percentage = serializers.FloatField(required=True)
    from_date = serializers.DateField(required=True)
    till = serializers.DateField(required=True)

    class Meta:
        model = Education
        fields = ['institute', 'stream', 'percentage', 'from_date', 'till']


class PerformanceSerializer(serializers.ModelSerializer):
    """
        This serializer is used to update score of a student
    """
    student = serializers.StringRelatedField(read_only=True)
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    update_by = serializers.StringRelatedField(read_only=True)
    score = serializers.FloatField(max_value=10, min_value=1)
    review_date = serializers.DateField(required=True)

    class Meta:
        model = Performance
        fields = ['student_id', 'student', 'course_id', 'course', 'mentor_id', 'mentor', 'score', 'week_no', 'remark',
                  'review_date', 'update_by']
        read_only_fields = ('student', 'week_no', 'mentor', 'course', 'update_by')

    def validate(self, data):
        data['update_by'] = self.context['user']
        return data


class ExcelDataSerializer(serializers.Serializer):
    """
        This serializer is used to validate data of a excel file
    """
    file = serializers.FileField(required=True)

    def validate(self, data):
        if data['file']._name.split('.')[1] not in ['xlsx']:
            raise serializers.ValidationError('Invalid file format. [.xlsx] expected')
        return data

class AddMentorSerializer(serializers.ModelSerializer):
    """
        This serializer is used to create new mentor user and assign course
    """
    mentor = CourseMentorSerializer(required=False)
    name = serializers.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile', 'mentor']


class MentorCourseSerializer(serializers.ModelSerializer):
    """
        This serailizer is used to get mentor-course details
    """
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Mentor
        fields = ['id','image', 'mentor_id', 'mid', 'mentor', 'course']

class GetMentorCourseDetailsSerializer(serializers.ModelSerializer):
    """
        This serailizer is used to get mentor-course details
    """
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Mentor
        fields = ['id','image', 'mentor_id', 'mid', 'mentor', 'course']


class AddStudentSerializer(serializers.ModelSerializer):
    """
        This serializer is used to create a new student user and assign course and mentor
    """
    student = StudentCourseMentorUpdateSerializer(required=False)
    name = serializers.CharField(max_length=50, required=False)
    mobile = serializers.RegexField("^[7-9]{1}[0-9]{9}$")

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile', 'student']


class PerformanceUpdateViaExcelSerializer(serializers.ModelSerializer):
    """
        This serializer is used to update student performance score from a excel file
    """
    class Meta:
        model = Performance
        fields = ['student', 'course', 'mentor', 'score', 'week_no', 'remark', 'review_date', 'update_by']
        read_only_fields = ('update_by',)

    def validate(self, data):
        data['update_by'] = self.context['user']
        return data
        

class MentorStudentCourseSerializer(serializers.Serializer):
    """
        This serializer is used to get student performance
    """
    mentor = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)
    student_id = serializers.StringRelatedField(read_only=True)
    student = serializers.StringRelatedField(read_only=True)
    week_no = serializers.StringRelatedField(read_only=True)
    score = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Performance
        read_only_fields = ('student_id')


