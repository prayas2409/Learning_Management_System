from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from rest_framework import authentication, status, generics, viewsets
from rest_framework.response import Response
from Auth.tasks import send_registration_mail
from Auth.JWTAuthentication import JWTAuth
from Auth.models import User, Roles
from .models import Course, Mentor, StudentCourseMentor, Student, Education, Performance
from django.utils.decorators import method_decorator
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from .serializer import *
import pandas
from .utils import ExcelHeader, ValueRange, Pattern, Configure
from .excel_validator import ExcelException, ExcelValidator
import sys

sys.path.append('..')
from Auth.permissions import isAdmin, isMentorOrAdmin, OnlyStudent
from Auth.middlewares import TokenAuthentication
from LMS.loggerConfig import log

from Management.utils import GeneratePassword, GetFirstNameAndLastName
from Management.serializer import *
from Auth.models import User, Roles


@method_decorator(TokenAuthentication, name='dispatch')
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


@method_decorator(TokenAuthentication, name='dispatch')
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


@method_decorator(TokenAuthentication, name='dispatch')
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


@method_decorator(TokenAuthentication, name='dispatch')
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


@method_decorator(TokenAuthentication, name='dispatch')
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


@method_decorator(TokenAuthentication, name='dispatch')
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
            return Response({'response': f'Course with this id {course_id} is not found'},
                            status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthentication, name='dispatch')
class MentorDetailsAPIView(GenericAPIView):
    serializer_class = MentorCourseSerializer
    permission_classes = [isAdmin]

    def get(self, request, mentor_id):
        """
            This API is used to get the Specific Mentor Profile if the user is mentor otherwise Admin can see each
            mentor's Profile
            @param mentor_id: mentor primary key @return: Specific Mentor Profile
        """
        try:
            mentor = Mentor.objects.get(mentor_id=mentor_id)
            mentorSerializerDict = dict(MentorCourseSerializer(mentor).data)
            userSerializer = UserSerializer(mentor.mentor)
            mentorSerializerDict.update(userSerializer.data)
            log.info("Mentor profile fected.")
            return Response({'response': mentorSerializerDict}, status=status.HTTP_200_OK)
        except Mentor.DoesNotExist:
            log.error("Mentor does not exist..!!")
            return Response({'response': f"Mentor with id {mentor_id} does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except KeyError as f:
            log.error(f)
            return Response({'response': 'user role doesnt exist'})
        except Exception as e:
            log.error(e)
            return Response({'response': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(TokenAuthentication, name='dispatch')
class StudentCourseMentorMapAPIView(GenericAPIView):
    serializer_class = StudentCourseMentorSerializer
    permission_classes = (isAdmin,)
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
        serializer = self.serializer_class(data=request.data, context={'user': request.META['user']})
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


@method_decorator(TokenAuthentication, name='dispatch')
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
            serializer = StudentCourseMentorUpdateSerializer(instance=student, data=request.data,
                                                             context={'user': request.META['user']})
            serializer.is_valid(raise_exception=True)
            mentor = serializer.validated_data.get('mentor')
            course = serializer.validated_data.get('course')
            if student.course_id == course.id:
                return Response({
                    'response': f"{course.course_name} is already assigned to {student.student.student.get_full_name()}."
                                f" Choose different one"}, status=status.HTTP_406_NOT_ACCEPTABLE)
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
            return Response({'response': f'record with id {student_id} does not exist'},
                            status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthentication, name='dispatch')
class GetMentorsForSpecificCourse(GenericAPIView):
    serializer_class = MentorCourseSerializer
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
            return Response({'response': f'course with id {course_id} does not exist'},
                            status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthentication, name='dispatch')
class StudentsAPIView(GenericAPIView):
    serializer_class = StudentSerializer
    permission_classes = [AllowAny, ]
    queryset = StudentCourseMentor.objects.all()

    def get(self, request):
        """Using this API Admin can see all course assigned students and mentor can see his course assigned students
         and student can see his own record
        """
        if request.META['user'].role == Roles.objects.get(role='mentor'):
            query = StudentCourseMentor.objects.filter(mentor=Mentor.objects.get(mentor_id=request.META['user']))
        elif request.META['user'].role == Roles.objects.get(role='student'):
            student = Student.objects.get(student_id=request.META['user'])
            query = StudentCourseMentor.objects.filter(student=student)
        else:
            query = self.queryset.all()
        if not query:
            if request.META['user'].role == Roles.objects.get(role='student'):
                student_serializer = StudentBasicSerializer(student)
                return Response({'response': student_serializer.data}, status=status.HTTP_200_OK)
            log.info("Records not found")
            return Response({'response': "Records not found"}, status=status.HTTP_404_NOT_FOUND)
        serializerDict = self.serializer_class(query, many=True).data
        log.info(f"records retrieved by {request.META['user'].role.role}")
        return Response({'response': serializerDict}, status=status.HTTP_200_OK)


@method_decorator(TokenAuthentication, name='dispatch')
class StudentDetailsAPIView(GenericAPIView):
    serializer_class = StudentDetailsSerializer
    permission_classes = [AllowAny]
    queryset = Student.objects.all()

    def get(self, request, student_id):
        """This API is used to get Student details as well ass eduction details. Admin can see any student, mentor can see
        those student under him and student can see his own details
        """
        try:
            if request.META['user'].role == Roles.objects.get(role='student'):
                student = Student.objects.get(student_id=request.META['user'])
            elif request.META['user'].role == Roles.objects.get(role='mentor'):
                student = StudentCourseMentor.objects.get(mentor=Mentor.objects.get(mentor_id=request.META['user']),
                                                          student_id=student_id).student
            else:
                student = self.queryset.get(id=student_id)
            serializer = dict(self.serializer_class(student).data)
            userSerializer = UserSerializer(student.student).data
            serializer.update(userSerializer)
            try:
                student = StudentCourseMentor.objects.get(student_id=student.id)
                studentCourseSerializer = CourseMentorSerializerDetails(student).data
                serializer.update(studentCourseSerializer)
            except StudentCourseMentor.DoesNotExist:
                pass
            log.info(f"Data accessed by {request.META['user'].role.role}")
            return Response({'response': serializer}, status=status.HTTP_200_OK)
        except (Student.DoesNotExist, StudentCourseMentor.DoesNotExist, Education.DoesNotExist):
            log.info('Record not found')
            return Response({'response': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthentication, name='dispatch')
class StudentsDetailsUpdateAPIView(GenericAPIView):
    serializer_class = StudentDetailsSerializer
    permission_classes = [OnlyStudent]
    queryset = Student.objects.all()

    def put(self, request):
        """This API is used to update student basic details
        """
        try:
            student = Student.objects.get(student_id=request.META['user'])
            serializer = self.serializer_class(instance=student, data=request.data)
            serializer.is_valid(raise_exception=True)
        except Student.DoesNotExist:
            return Response({'response': "Records not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            serializer.save()
        except Exception:
            log.info('Some error occurred')
            return Response({'response': "Some error occurred "}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        log.info('Record updated by ' + request.META['user'].role.role)
        return Response({'response': 'Records updated'}, status=status.HTTP_200_OK)


@method_decorator(TokenAuthentication, name='dispatch')
class EducationDetails(GenericAPIView):
    serializer_class = EducationSerializer
    permission_classes = [AllowAny]
    queryset = Education.objects.all()

    def get(self, request, student_id):
        """Using this API admin can see any students educational details, mentor can see his own students details
        student can see his own details
        """
        try:
            if request.META['user'].role == Roles.objects.get(role='student'):
                student = Student.objects.get(student_id=request.META['user'].id)
                query = self.queryset.filter(student_id=student.id)
            elif request.META['user'].role == Roles.objects.get(role='mentor'):
                mentor = Mentor.objects.get(mentor_id=request.META['user'].id)
                query = self.queryset.filter(mentor_id=mentor, student_id=student_id)
            else:
                query = self.queryset.filter(student_id=student_id)

            serializer = self.serializer_class(query, many=True)
            if not serializer.data:
                log.info('serializer data is empty')
                return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'response': serializer.data}, status=status.HTTP_200_OK)
        except (Mentor.DoesNotExist, Student.DoesNotExist) as e:
            log.error(e)
            return Response({'response': "Records not found"}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthentication, name='dispatch')
class EducationDetailsAdd(GenericAPIView):
    serializer_class = EducationSerializer
    permission_classes = [OnlyStudent]
    queryset = Education.objects.all()

    def post(self, request):
        """This API is used to add Education details of student. This API is accessible to student only
        """
        try:
            student = Student.objects.get(student_id=request.META['user'].id)
            serializer = self.serializer_class(data=request.data, context={'student': student.id})
            serializer.is_valid(raise_exception=True)
            degree = serializer.validated_data.get('degree')
            Education.objects.get(student_id=student.id, degree=degree)
            log.info('data is already present in database')
            return Response({'response': f"{degree} data is already saved"}, status=status.HTTP_208_ALREADY_REPORTED)
        except Education.DoesNotExist:
            serializer.save()
            log.info('data is saved')
            return Response({'response': f"{degree} data is saved"}, status=status.HTTP_201_CREATED)
        except Student.DoesNotExist as e:
            log.error(e)
            return Response({'response': 'Student record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log.error(e)
            return Response({'response': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(TokenAuthentication, name='dispatch')
class EducationDetailsUpdate(GenericAPIView):
    serializer_class = EducationUpdateSerializer
    permission_classes = [OnlyStudent]
    queryset = Education.objects.all()

    def patch(self, request, record_id):
        """This API is used to update student educational details
         @param record_id : Education table's primary key
         @return: updates existing education record
        """
        try:
            student = Student.objects.get(student_id=request.META['user'].id)
            record = self.queryset.get(id=record_id, student_id=student.id)
            serializer = self.serializer_class(instance=record, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            log.info(f"{record.degree} record is updated")
            return Response({'response': f"{record.degree} records is update"}, status=status.HTTP_200_OK)
        except (Student.DoesNotExist, Education.DoesNotExist) as e:
            log.error(e)
            return Response({'response': "Records not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log.error(e)
            return Response({'response': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(TokenAuthentication, name='dispatch')
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
        log.info('Records Retrieved by ' + request.META['user'].role.role)
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(TokenAuthentication, name='dispatch')
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
            if request.META['user'].role == Roles.objects.get(role='student'):
                student = Student.objects.get(student_id=request.META['user'].id)
                query = self.queryset.filter(student_id=student.id)
            elif request.META['user'].role == Roles.objects.get(role='mentor'):
                mentor = Mentor.objects.get(mentor_id=request.META['user'].id)
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
        return Response({'response': serializer.data}, status=status.HTTP_200_OK)


@method_decorator(TokenAuthentication, name='dispatch')
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
            if request.META['user'].role == Roles.objects.get(role='mentor'):
                mentor = Mentor.objects.get(mentor_id=request.META['user'].id)
                student = self.queryset.get(mentor_id=mentor.id, student_id=student_id, week_no=week_no)
            else:
                student = self.queryset.get(student_id=student_id, week_no=week_no)

            serializer = self.serializer_class(instance=student, data=request.data,
                                               context={'user': request.META['user']})
            serializer.is_valid(raise_exception=True)
            if week_no > 1:
                previous_record = self.queryset.get(student_id=student_id, week_no=week_no - 1).score
                if not previous_record:
                    log.info('Need to update previous weeks first')
                    return Response({'response': f'Need to update previous weeks first'},
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
        except (Performance.DoesNotExist, Student.DoesNotExist, Mentor.DoesNotExist):
            log.info('Records not found')
            return Response({'response': 'Records not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {'response': f"Score updated for {student.student.student.get_full_name()}'s week {week_no} review"},
            status=status.HTTP_200_OK)


@method_decorator(TokenAuthentication, name='dispatch')
class UpdateScoreFromExcel(GenericAPIView):
    serializer_class = ExcelDataSerializer
    permission_classes = [isMentorOrAdmin]

    def post(self, request):
        try:
            file = request.FILES.get('file')
            serializer = self.serializer_class(data={'file': file})
            if serializer.is_valid():
                file = serializer.validated_data['file']
                df = pandas.read_excel(file)
                role = request.META.get('user').role
                ExcelValidator.validateExcel(df, role)  # Validating the excel file
                error_message = {}
                for row_no, row in enumerate(df.iterrows()):
                    try:
                        if request.META.get('user').role == Roles.objects.get(role='mentor'):
                            mentor_id = request.META.get('user').mentor.id
                        else:
                            mentor_id = Mentor.objects.get(mid=row[1][-2]).id
                        data = Configure.get_configured_excel_data(row, mentor_id)  # configuring excel data
                        serializer = PerformanceUpdateViaExcelSerializer(data=data,
                                                                         context={'user': request.META.get('user')})
                        if serializer.is_valid():
                            student = serializer.validated_data['student']
                            course = serializer.validated_data['course']
                            mentor = serializer.validated_data['mentor']
                            week_no = serializer.validated_data['week_no']
                            map_obj = StudentCourseMentor.objects.get(student=student)
                            duplicate_entry = False
                            performance_list = Performance.objects.filter(student=student)
                            for performance in performance_list:
                                # checking duplicate entry
                                if performance.student == student and performance.week_no == week_no and performance.course == course:
                                    error_message[
                                        f"Row_no-{row_no + 1}"] = 'Duplicate Entry found, Data is already saved'
                                    duplicate_entry = True
                            if not duplicate_entry:
                                # checking student mentor course mapping
                                if map_obj.course == course and map_obj.mentor == mentor and course in mentor.course.all():
                                    serializer.save()
                                else:
                                    error_message[
                                        f"Row_no-{row_no + 1}"] = 'course-mentor-student mapping does not exist'
                            else:
                                pass
                        else:
                            error_message[f"Row_no-{row_no + 1}"] = serializer.errors
                    except (Student.DoesNotExist, Mentor.DoesNotExist, StudentCourseMentor.DoesNotExist,
                            Course.DoesNotExist) as e:
                        error_message[f"Row_no-{row_no + 1}"] = str(e)
                if error_message:
                    msg = 'Record Partially updated! ' + str(error_message)
                    log.error(str(error_message))
                else:
                    msg = 'Record updated successfully'
                return Response({"response": msg}, status=status.HTTP_200_OK)
            log.error(serializer.errors)
            return Response({'response': serializer.errors["non_field_errors"][0]}, status=status.HTTP_400_BAD_REQUEST)
        except ExcelException as e:
            log.error(str(e))
            return Response({'response': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log.error(str(e))
            return Response({'response': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(TokenAuthentication, name='dispatch')
class AddMentorAPIView(GenericAPIView):
    """ This API is used for add mentor"""
    permission_classes = [isAdmin]
    serializer_class = MentorDetailSerializer

    def post(self, request):
        """
        This function is used for adding mentor with course
        :param request: mentors details
        :return: add mentor
        """
        try :
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid()
            name = serializer.data.get('name')
            email = serializer.data.get('email')
            mobile = serializer.data.get('mobile')
            first_name = GetFirstNameAndLastName.get_first_name(name)
            last_name = GetFirstNameAndLastName.get_last_name(name)
            password = GeneratePassword.generate_password(self)
            user = User.objects.create_user(username=email, first_name=first_name, last_name=last_name, email=email,
                                            password=password, mobile=mobile, role=Roles.objects.get(role='mentor'))
            mentor = Mentor.objects.get(mentor=user)
            data = {
                'name': user.get_full_name(),
                'username': user.username,
                'password': password,
                'email': user.email,
                'site': get_current_site(request).domain,
            }
            send_registration_mail.delay(data)
            courses = serializer.data['mentor'].get('course')
            for course_id in courses:
                for mentor_course in mentor.course.all():
                    if course_id == mentor_course.id:
                        log.info('duplicate entry found')
                        return Response({'response': 'This course is already added'},
                                        status=status.HTTP_400_BAD_REQUEST)
                mentor.course.add(course_id)
                mentor.save()
            log.info('New Mentor is added')
            return Response({'response': f"{mentor} has been added as a Mentor"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            log.error(e)
            return Response({'response':"Mentor already exists."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log.error(e)
            return Response({'response':'Something went wrong!!!'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(TokenAuthentication, name='dispatch')
class GetMentorDetailsAPIView(GenericAPIView):
    """ This API used for fetching mentor details"""
    serializer_class = MentorCourseSerializer
    permission_classes = [isMentorOrAdmin]

    def get_student_count_in_course_list(self, mentor):
        """
        This function is used for fetching the mentors details
        :param mentor: mentor
        :return: return student count
        """
        courses = mentor.course.all()
        course_list = []
        for course in courses:
            student = StudentCourseMentor.objects.filter(mentor=mentor, course=course).count()
            course_list.append({"course_name": str(course), "student_count": student})
        return course_list

    def get(self, request):
        """
        This function is used for fetching mentor details
        :return: mentor details
        """
        try:
            if request.META['user'].role == Roles.objects.get(role='admin'):
                mentors = Mentor.objects.all()
                if len(mentors) == 0:
                    log.info("Mentors list empty")
                    return Response({'response': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    mentor_list = []
                    for mentor in mentors:
                        serializer = dict(self.serializer_class(mentor).data)
                        course_list = self.get_student_count_in_course_list(mentor)
                        serializer.update({"course": course_list})
                        mentor_list.append(serializer)
                    log.info("Mentors retrieved")
                    return Response({'response': mentor_list}, status=status.HTTP_200_OK)
            elif request.META['user'].role == Roles.objects.get(role='mentor'):
                mentor = Mentor.objects.get(mentor=request.META['user'])
                serializer = dict(self.serializer_class(mentor).data)
                course_list = self.get_student_count_in_course_list(mentor)
                serializer.update({"course": course_list})
                log.info("Mentor details retrieved")
                return Response({'response': serializer}, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            return Response({'response': 'Something went wrong'}, status=status.HTTP_403_FORBIDDEN)


@method_decorator(TokenAuthentication, name='dispatch')
class AddStudent(GenericAPIView):
    """
        This API is used to Add new user student and mapp mentor, course to it
    """
    serializer_class = AddStudentSerializer
    permission_classes = [isAdmin]

    def post(self, request):
        """
        This function is used for adding student with course and mentor
        :param request: student details
        :return: add student
        """
        try:
            serializer = self.serializer_class(data=request.data, context={'user': request.META['user']})
            serializer.is_valid(raise_exception=True)
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            mobile = serializer.validated_data['mobile']
            first_name = GetFirstNameAndLastName.get_first_name(name)
            last_name = GetFirstNameAndLastName.get_last_name(name)
            password = GeneratePassword.generate_password(self)
            student = serializer.validated_data['student']
            course = student['course']
            mentor = student['mentor']
            if mentor and course:
                if course in mentor.course.all():
                    user = User.objects.create_user(username=email, first_name=first_name, last_name=last_name,
                                                    email=email, mobile=mobile, role=Roles.objects.get(role='student'),
                                                    password=password)
                    StudentCourseMentor.objects.create(student=Student.objects.get(student=user),
                                                       course=course,
                                                       mentor=Mentor.objects.get(
                                                           mentor=User.objects.get(mentor=mentor)))
                    data = {
                        'name': user.get_full_name(),
                        'username': user.username,
                        'password': password,
                        'email': user.email,
                        'site': get_current_site(request).domain,
                    }
                    send_registration_mail.delay(data)
                    log.info("Student is created succesfully")
                    return Response({'response': "Student is created succesfully"}, status=status.HTTP_201_CREATED)
                log.error('This course is not assigned to the mentor.')
                return Response({'response': f'{course.course_name} is not assigned to the mentor.'},
                                status=status.HTTP_400_BAD_REQUEST)
            log.error('Please provide the course and mentor details.')
            return Response({'response': 'Please provide the course and mentor details.'})
        except Exception as e:
            log.error(e)
            return Response({'response': 'Something went wrong!!!'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(TokenAuthentication, name='dispatch')
class Studentprofile(GenericAPIView):
    """
    This api will show the profile data of students
    Retrieved by student id
    Accessible by admin,student and for mentors only assigned students under him/her.
    """
    serializer_class = StudentProfileDetails
    permission_classes = [AllowAny]
    queryset = Student.objects.all()

    def get(self, request, student_id):

        try:
            if request.META['user'].role == Roles.objects.get(role='student'):
                student = Student.objects.get(student_id=request.META['user'])
            elif request.META['user'].role == Roles.objects.get(role='mentor'):
                student = StudentCourseMentor.objects.get(mentor=Mentor.objects.get(mentor_id=request.META['user']),
                                                          student_id=student_id).student
            else:
                student = self.queryset.get(id=student_id)
            serializer = dict(self.serializer_class(student).data)
            userSerializer = UserSerializer(student.student).data
            serializer.update({'USER_DATA': userSerializer})

            EducationDetails = EducationSerializer1(student.student).data
            serializer.update({'Education_Details': EducationDetails})
            student = StudentCourseMentor.objects.get(student_id=student.id)
            studentCourseSerializer = CourseMentorSerializers(student).data
            serializer.update({'Mentor&Course': studentCourseSerializer})
            log.info(f"Data accessed by {request.META['user'].role.role}")
            return Response({'response': serializer}, status=status.HTTP_200_OK)
        except (Student.DoesNotExist, StudentCourseMentor.DoesNotExist):
            log.info('Record not found')
            return Response({'response': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthentication, name='dispatch')
class MentorStudentCourse(GenericAPIView):
    serializer_class = MentorStudentCourseSerializer
    permission_classes = [isAdmin]
    queryset = Performance.objects.all()

    def get(self, request, mentor_id, course_id):
        """
            This API is used to get the list of students according to mentor_id and course_id
            @param mentor_id: mentor primary key
            @param course_id: course primary key
            @return: List of Students
        """
        try:
            query = self.queryset.filter(mentor_id=mentor_id, course_id=course_id)
            serializer = self.serializer_class(query, many=True)

            if not serializer.data:
                log.error('serializer data is empty, from get_MentorStudentCourse()')
                return Response({'response': 'Records not found, check mentor_id/Course_id..!!'},
                                status=status.HTTP_404_NOT_FOUND)
            log.info("Fetched List of Students according to Mentor_id and Course_id, from get_MentorStudentCourse() ")
            return Response({'response': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e, "from get_MentorStudentCourse()")
            return Response("Something went wrong", status=status.HTTP_400_BAD_REQUEST)
