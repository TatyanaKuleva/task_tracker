from rest_framework import viewsets
from rest_framework.generics import CreateAPIView

from .models import User
from .serializers import RegisterSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
