from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, UserCreateSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=request.data.get('username'))
            if not user.is_active:
                return Response({'error': 'Tài khoản chưa được kích hoạt, vui lòng kích hoạt tài khoản'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if user.is_deactivated:
                return Response({'error': 'Account deactivated'}, status=status.HTTP_401_UNAUTHORIZED)
            if not user.check_password(request.data.get('password')):
                return Response({'error': 'Sai tài khoản hoặc mật khẩu'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Tài khoản không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)
