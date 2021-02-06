from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from .models import Course, Mentor, StudentCourseMentor, Student, Education, Performance
from django.utils.decorators import method_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from .serializers import CourseSerializer, CourseMentorSerializer, MentorSerializer, UserSerializer, \
    StudentCourseMentorSerializer, StudentCourseMentorReadSerializer, StudentCourseMentorUpdateSerializer,\
    StudentSerializer, StudentBasicSerializer, StudentDetailsSerializer, EducationSerializer, CourseMentorSerializerDetails, \
    NewStudentsSerializer, PerformanceSerializer

import sys
sys.path.append('..')
from Auth.permissions import isAdmin, isMentorOrAdmin, OnlyStudent, Role
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
        student = serializer.validated_data.get('student')

        if mentor is None or course is None:
            return Response({'response': "Mentor or Course can not be Null"}, status=status.HTTP_400_BAD_REQUEST)
        if course in mentor.course.all():
            serializer.save()
            student.course_assigned = True
            student.save()
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

    def put(self, request, student_id):
        """This API is used to update student course mentor mapping
        @param request: Course id and mentor id
        @param record_id: record id of StudentCourseMentor model
        @return: updates record
        """
        try:
            student = self.queryset.get(student_id=student_id)
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
            return Response({'response': f'record with id {student_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)


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
        if request.user.role == Role.MENTOR.value:
            query = StudentCourseMentor.objects.filter(mentor=Mentor.objects.get(mentor_id=request.user))
        elif request.user.role == Role.STUDENT.value:
            student = Student.objects.get(student_id=request.user)
            query = StudentCourseMentor.objects.filter(student=student)
        else:
            query = self.queryset.all()
        if not query:
            if request.user.role == Role.STUDENT.value:
                student_serializer = StudentBasicSerializer(student)
                return Response({'response': student_serializer.data}, status=status.HTTP_200_OK)
            log.info("Records not found")
            return Response({'response': "Records not found"}, status=status.HTTP_404_NOT_FOUND)
        serializerDict = self.serializer_class(query, many=True).data
        log.info(f"records retrieved by {request.user.role}")
        return Response({'response': serializerDict}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentDetailsAPIView(GenericAPIView):
    serializer_class = StudentDetailsSerializer
    permission_classes = [AllowAny]
    queryset = Student.objects.all()

    def get(self, request, student_id):
        """This API is used to get Student details as well ass eduction details. Admin can see any student, mentor can see
        those student under him and student can see his own details
        """
        basic_details_flag = True
        if request.resolver_match.url_name == 'education-details':
            basic_details_flag = False
            self.serializer_class = EducationSerializer
            self.queryset = Education.objects.all()

        try:
            if request.user.role == Role.STUDENT.value:
                if basic_details_flag:
                    student = Student.objects.get(student_id=request.user)
                else:
                    student = Education.objects.get(student_id=Student.objects.get(student_id=request.user))
            elif request.user.role == Role.MENTOR.value:
                student = StudentCourseMentor.objects.get(mentor=Mentor.objects.get(mentor_id=request.user),
                                                          student_id=student_id).student
                if not basic_details_flag:
                    student = Education.objects.get(student_id=student.id)
            else:
                student = self.queryset.get(id=student_id)
            serializer = dict(self.serializer_class(student).data)
            if basic_details_flag:
                userSerializer = UserSerializer(student.student).data
                serializer.update(userSerializer)
                try:
                    student = StudentCourseMentor.objects.get(student_id=student.id)
                    studentCourseSerializer = CourseMentorSerializerDetails(student).data
                    serializer.update(studentCourseSerializer)
                except StudentCourseMentor.DoesNotExist:
                    pass
            log.info(f"Data accessed by {request.user.role}")
            return Response({'response': serializer}, status=status.HTTP_200_OK)
        except (Student.DoesNotExist, StudentCourseMentor.DoesNotExist, Education.DoesNotExist):
            log.info('Record not found')
            return Response({'response': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentsDetailsUpdateAPIView(GenericAPIView):
    serializer_class = StudentDetailsSerializer
    permission_classes = [OnlyStudent]
    queryset = Student.objects.all()

    def get(self, request):
        """This API is used to inform the client to serve the desired page
        """
        page_code = 100
        if request.resolver_match.url_name == 'education-details-update':
            self.serializer_class = EducationSerializer
            page_code = 200
        response = {
            'page_code': page_code,
            'url': request.path
        }
        log.info('Response is sent client')
        return Response({'response': response})

    def put(self, request):
        """This API is used to update student basic details as well as education details
        """
        basic_details_flag = True
        if request.resolver_match.url_name == 'education-details-update':
            self.serializer_class = EducationSerializer
            self.queryset = Education.objects.all()
            basic_details_flag = False

        student = Student.objects.get(student_id=request.user)
        if not basic_details_flag:
            student = Education.objects.get(student_id=student.id)

        serializer = self.serializer_class(instance=student, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception:
            log.info('Some error occurred')
            return Response({'response': "Some error occurred "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        log.info(f'Record updated by {request.user.role}')
        return Response({'response': 'Records updated'}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class NewStudents(GenericAPIView):
    serializer_class = NewStudentsSerializer
    permission_classes = [isAdmin]
    queryset = Student.objects.all()

    def get(self, request):
        """Using this API admin will retrieve new students who have not been assigned to any course yet
        @return : returns list of new students data
        """
        query = self.queryset.filter(course_assigned=False)
        serializer = self.serializer_class(query, many=True)
        if not serializer.data:
            log.info('No records found')
            return Response({'response': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
        log.info(f'Records Retrieved by {request.user.role}')
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentPerformance(GenericAPIView):
    serializer_class = PerformanceSerializer
    permission_classes = [AllowAny]
    queryset = Performance.objects.all()

    def get(self, request, student_id):
        """Using this API student can see his own all performance, mentor can see all students performance under him
        and admin can see any students all performance
        @param request: get request
        @param student_id: students table's primary key
        @return: performace records of specific student
        """
        try:
            if request.user.role == Role.STUDENT.value:
                student = Student.objects.get(student_id=request.user.id)
                query = self.queryset.filter(student_id=student.id)
            elif request.user.role == Role.MENTOR.value:
                mentor = Mentor.objects.get(mentor_id=request.user.id)
                query = self.queryset.filter(mentor_id=mentor.id, student_id=student_id)
            else:
                query = self.queryset.filter(student_id=student_id)
            serializer = self.serializer_class(query, many=True)
        except (Student.DoesNotExist, Mentor.DoesNotExist):
            log.info('Records not found')
            return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
        if not serializer.data:
            log.info('Records not found')
            return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
        log.info(f'Records retrieved by {request.user.role}')
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(SessionAuthentication, name='dispatch')
class StudentPerfromanceUpdate(GenericAPIView):
    serializer_class = PerformanceSerializer
    permission_classes = [isMentorOrAdmin]
    queryset = Performance.objects.all()

    def put(self, request, student_id, week_no):
        """This API is used to update student's weekly performance either by mentor or admin
        @param request: score, review_date
        @param student_id: student primary key
        @param week_no: review week number
        @return: updates score
        """
        try:
            if request.user.role == Role.MENTOR.value:
                mentor = Mentor.objects.get(mentor_id=request.user.id)
                student = self.queryset.get(mentor_id=mentor.id, student_id=student_id, week_no=week_no)
            else:
                student = self.queryset.get(student_id=student_id, week_no=week_no)

            serializer = self.serializer_class(instance=student, data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            if week_no > 1:
                previous_record = self.queryset.get(student_id=student_id, week_no=week_no-1).score
                if not previous_record:
                    log.info('Need to update previous weeks first')
                    return Response({'response': f'Need to update previous weeks first'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except (Performance.DoesNotExist, Student.DoesNotExist, Mentor.DoesNotExist):
            log.info('Records not found')
            return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'response': f"Score updated for {student.student.student.get_full_name()}'s week {week_no} review"},
                        status=status.HTTP_200_OK)


