from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from .models import Course
from django.utils.decorators import method_decorator
from rest_framework.generics import GenericAPIView
from .serializers import AddCourseSerializer

import sys
sys.path.append('..')
from Auth.permissions import isAdmin
from Auth.middlewares import SessionAuthentication
from LMS.loggerConfig import log


@method_decorator(SessionAuthentication, name='dispatch')
class AddCourseAPIView(GenericAPIView):
    serializer_class = AddCourseSerializer
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
            return Response({'response': f"{serializer.data.get('course_name')} is already present"},status=status.HTTP_400_BAD_REQUEST)
        log.info('Course is added')
        return Response({'response': f"{serializer.data.get('course_name')} is added in course"}, status=status.HTTP_201_CREATED)

