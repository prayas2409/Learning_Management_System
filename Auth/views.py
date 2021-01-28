from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .serializers import UserSerializer
from .permissions import isAdmin


class UserRegistrationView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (isAdmin,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'response': f"user is added"}, status=status.HTTP_201_CREATED)
