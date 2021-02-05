from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from .models import Course, Mentor, StudentCourseMentor, Student
from django.utils.decorators import method_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from .serializers import CourseSerializer, CourseMentorSerializer, MentorSerializer, UserSerializer, \
    StudentCourseMentorSerializer, StudentCourseMentorReadSerializer, StudentCourseMentorUpdateSerializer,\
    StudentSerializer, StudentBasicSerializer, StudentDetailsSerializer, EducationSerializer

import sys
sys.path.append('..')
from Auth.permissions import isAdmin, isMentorOrAdmin
from Auth.middlewares import SessionAuthentication
from LMS.loggerConfig import log


@method_decorator(SessionAuthentication, name='dispatch')
class AddCourseAPIView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [isAdmin]

    def post(self, request):
        """This API is used to add course by the admin
        @param request: course_name
        @return: save course in the database
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except IntegrityError:
            log.info('duplicate course entry is blocked')
            return Response({'response': f"{serializer.data.get('course_name')} is already present"},
                            status=status.HTTP_400_BAD_REQUEST)
        log.info('Course is added')
        return Response({'response': f"{serializer.data.get('course_name')} is added in course"},
                        status=status.HTTP_201_CREATED)


@method_decorator(SessionAuthentication, name='dispatch')
class AllCoursesAPIView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [isAdmin]
    queryset = Course.objects.all()

    def get(self, request):
        """This API is used to retrieve all courses by admin
        @return: returns all courses
        """
        serializer = self.serializer_class(self.queryset.all(), many=True)
        log.info('All courses are retrieved')
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class UpdateCourseAPIView(GenericAPIView):
    permission_classes = [isAdmin]
    serializer_class = CourseSerializer

    def put(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            serializer = self.serializer_class(instance=course, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'response': 'Course is updated'}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            log.info('course not found')
            return Response({'response': 'Course with given id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            log.info('duplicate course entry is blocked')
            return Response({'response': f"{serializer.data.get('course_name')} is already present"},
                            status=status.HTTP_400_BAD_REQUEST)


@method_decorator(SessionAuthentication, name='dispatch')
class DeleteCourseAPIView(GenericAPIView):
    serializer_class = CourseSerializer
    permission_classes = [isAdmin]

    def delete(self, request, id):
        """This API is used to delete course by id by admin
        @return: deletes course from database
        """
        try:
            course = Course.objects.get(id=id)
            course.delete()
            return Response({'response': f"{course.course_name} is deleted"})
        except Course.DoesNotExist:
            log.info("course not found")
            return Response({'response': 'Course not found with this id'})


@method_decorator(SessionAuthentication, name='dispatch')
class CourseToMentorMapAPIView(GenericAPIView):
    permission_classes = [isAdmin]
    serializer_class = CourseMentorSerializer

    def put(self, request, mentor_id):
        """This API is used to update course to mentor"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            mentor = Mentor.objects.get(id=mentor_id)
        except Mentor.DoesNotExist:
            log.info('mentor does not exist')
            return Response({'response': 'Mentor id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        for course_id in serializer.data.get('course'):
            for mentor_course in mentor.course.all():
                if course_id == mentor_course.id:
                    log.info('duplicate entry found')
                    return Response({'response': 'This course is already added'}, status=status.HTTP_400_BAD_REQUEST)
            mentor.course.add(course_id)
        log.info('new course added to mentor')
        return Response({'response': f" New course added to {mentor}'s course list"})


@method_decorator(SessionAuthentication, name='dispatch')
class DeleteCourseFromMentorListAPIView(GenericAPIView):
    permission_classes = [isAdmin]

    def delete(self, request, mentor_id, course_id):
        """This API is used to delete course from mentor list
        """
        try:
            mentor = Mentor.objects.get(id=mentor_id)
            course = Course.objects.get(id=course_id)
            if course in mentor.course.all():
                mentor.course.remove(course_id)
                log.info('Course removed')
                return Response({'response': f"{course.course_name} is removed"}, status=status.HTTP_200_OK)
            return Response(
                {'response': f"{course.course_name} is not in {mentor.mentor.get_full_name()}'s course list"},
                status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            log.info('mentor does not exist')
            return Response({'response': 'Mentor id does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Course.DoesNotExist:
            log.info(f'Course with id {course_id} not found')
            return Response({'response': f'Course with this id {course_id} is not found'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(SessionAuthentication, name='dispatch')
class AllMentorDetailsAPIView(GenericAPIView):
    serializer_class = MentorSerializer
    permission_classes = [isAdmin]
    queryset = Mentor.objects.all()

    def get(self, request):
        serializer = self.serializer_class(self.queryset.all(), many=True)
        if len(serializer.data) == 0:
            log.info("Mentors list empty")
            return Response({'response': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
        log.info("Mentors retrieved")
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class MentorDetailsAPIView(GenericAPIView):
    serializer_class = MentorSerializer
    permission_classes = [isAdmin]

    def get(self, request, mentor_id):
        try:
            mentor = Mentor.objects.get(id=mentor_id)
            mentorSerializerDict = dict(MentorSerializer(mentor).data)
            userSerializer = UserSerializer(mentor.mentor)
            mentorSerializerDict.update(userSerializer.data)
            return Response({'response': mentorSerializerDict}, status=status.HTTP_200_OK)
        except Mentor.DoesNotExist:
            return Response({'response': f"Mentor with id {mentor_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'response': 'something wrong happend'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentCourseMentorMapAPIView(GenericAPIView):
    serializer_class = StudentCourseMentorSerializer
    permission_classes = [isAdmin]
    queryset = StudentCourseMentor.objects.all()

    def get(self, request):
        """This API is used to get student course mentor mapped records
        """
        serializer = StudentCourseMentorReadSerializer(self.queryset.all(), many=True)
        if not serializer.data:
            log.info('Records not found')
            return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
        log.info('student course mentor mapped records fetched')
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        """This API is used to post student course mentor mapped record
        """
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        mentor = serializer.validated_data.get('mentor')
        course = serializer.validated_data.get('course')
        if mentor is None or course is None:
            return Response({'response': "Mentor or Course can not be Null"}, status=status.HTTP_400_BAD_REQUEST)
        if course in mentor.course.all():
            serializer.save()
            log.info('Record added')
            return Response({'response': "Record added"}, status=status.HTTP_200_OK)
        log.info('course not in mentor bucket')
        return Response({'response:': f"{course.course_name} is not in {mentor.mentor.get_full_name()}'s bucket"}
                        , status=status.HTTP_404_NOT_FOUND)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentCourseMentorUpdateAPIView(GenericAPIView):
    serializer_class = StudentCourseMentorUpdateSerializer
    permission_classes = [isAdmin]
    queryset = StudentCourseMentor.objects.all()

    def put(self, request, record_id):
        """This API is used to update student course mentor mapping
        @param request: Course id and mentor id
        @param record_id: record id of StudentCourseMentor model
        @return: updates record
        """
        try:
            student = self.queryset.get(id=record_id)
            serializer = StudentCourseMentorUpdateSerializer(instance=student, data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            mentor = serializer.validated_data.get('mentor')
            course = serializer.validated_data.get('course')
            if mentor is None or course is None:
                return Response({'response': "Mentor or Course can not be Null"}, status=status.HTTP_400_BAD_REQUEST)
            if course in mentor.course.all():
                serializer.save()
                log.info('record updated')
                return Response({'response': "Record updated"}, status=status.HTTP_200_OK)
            return Response({'response:': f"{course.course_name} is not in {mentor.mentor.get_full_name()}'s bucket"},
                            status=status.HTTP_404_NOT_FOUND)
        except StudentCourseMentor.DoesNotExist:
            log.info("record id not found")
            return Response({'response': f'record with id {record_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(SessionAuthentication, name='dispatch')
class GetMentorsForSpecificCourse(GenericAPIView):
    serializer_class = MentorSerializer
    permission_classes = [isAdmin]

    def get(self, request, course_id):
        """This API is used to fetch course oriented mentors
        """
        try:
            course = Course.objects.get(id=course_id)
            mentors = course.course_mentor.all()
            serializer = self.serializer_class(mentors, many=True)
            if not serializer.data:
                log.info('Records not found')
                return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
            log.info('mentor records of course is fetched')
            return Response({'response': serializer.data}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'response': f'course with id {course_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentsAPIView(GenericAPIView):
    serializer_class = StudentSerializer
    permission_classes = [AllowAny,]
    queryset = StudentCourseMentor.objects.all()

    def get(self, request):
        """Using this API Admin can see all course assigned students and mentor can see his course assigned students
         and student can see his own record
        """
        if request.user.role == 'Mentor':
            query = StudentCourseMentor.objects.filter(mentor=Mentor.objects.get(mentor_id=request.user))
        elif request.user.role == 'Engineer':
            student = Student.objects.get(student_id=request.user)
            query = StudentCourseMentor.objects.filter(student=student)
        else:
            query = self.queryset.all()
        if not query:
            if request.user.role == "Engineer":
                student_serializer = StudentBasicSerializer(student)
                return Response({'response': student_serializer.data}, status=status.HTTP_200_OK)
            log.info("Records not found")
            return Response({'response': "Records not found"}, status=status.HTTP_404_NOT_FOUND)
        serializerDict = self.serializer_class(query, many=True).data
        log.info(f"records retrieved by {request.user.role}")
        return Response({'response': serializerDict}, status=status.HTTP_200_OK)


class StudentDetailsAPIView(GenericAPIView):
    serializer_class = StudentDetailsSerializer
    permission_classes = [AllowAny]
    queryset = Student.objects.all()

    def get(self, request, student_id):
        """This API is used to get Student details as well ass eduction details. Admin can see any student, mentor can see
        those student under him and student can see his own details
        """
        if request.resolver_match.url_name == 'education-details':
            self.serializer_class = EducationSerializer
        try:
            if request.user.role == "Engineer":
                student = Student.objects.get(student_id=request.user)
            elif request.user.role == "Mentor":
                student = StudentCourseMentor.objects.get(mentor=Mentor.objects.get(mentor_id=request.user),
                                                          student_id=student_id).student
            else:
                student = Student.objects.get(id=student_id)
            serializer = self.serializer_class(student)
            log.info(f"Data accessed by {request.user.role}")
            return Response({'response': serializer.data}, status=status.HTTP_200_OK)
        except (Student.DoesNotExist, StudentCourseMentor.DoesNotExist):
            log.info('Record not found')
            return Response({'response': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)