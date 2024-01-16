from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

user = get_user_model()


# creating new users


class UserCreateSerializer(BaseUserCreateSerializer):
    username = serializers.CharField(max_length=155, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Tài khoản đã tồn tại")])
    email = serializers.EmailField(max_length=254, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Đã tồn tại email")])

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']

    # def create(self, validated_data):
    #     User = super().create(validated_data)
    #     return User


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'first_name',
                  'last_name', 'email',
                  'username',
                  'is_active',
                  'is_deactivated',
                  ]

    # this is where we send a request to slash me/ or auth/users
    def validate(self, attrs):
        validated_attr = super().validate(attrs)
        username = validated_attr.get('username')

        users = user.objects.get(username=username)

        if users.is_deactivated:
            raise ValidationError(
                'Account deactivated')

        if not users.is_active:
            raise ValidationError(
                'Account not activated')

        return validated_attr


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        obj = self.user

        data.update({
            'id': obj.id, 'first_name': obj.first_name,
            'last_name': obj.last_name, 'email': obj.email,
            'username': obj.username,
            'is_staff': obj.is_staff,
            'is_active': obj.is_active,
            'is_deactivated': obj.is_deactivated,
            'address': obj.address,
            'phone_number': obj.phone_number
        })

        return data
