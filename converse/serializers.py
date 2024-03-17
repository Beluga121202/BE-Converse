from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer, \
    ActivationSerializer as BaseActivationSerializer, UserFunctionsMixin, \
    SendEmailResetSerializer as BaseSendEmailResetSerializer
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from converse.models import Product, Banner, Order, OrderDetails, User

user = get_user_model()


# creating new users


class UserCreateSerializer(BaseUserCreateSerializer):
    username = serializers.CharField(max_length=155, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Tài khoản đã tồn tại")])
    email = serializers.EmailField(max_length=254, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Đã tồn tại email")])
    phone_number = serializers.CharField(max_length=254, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Số điện thoại đã được sử dụng")])

    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'phone_number', 'address', 'gender',
                  'birthday']

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
            'phone_number': obj.phone_number,
            'gender': obj.gender,
            'birth_date': obj.birthday
        })

        return data


class ActivationSerializer(BaseActivationSerializer):
    default_error_messages = {
        "stale_token": 'Tài khoản đã được kích hoạt'
    }


class SendEmailResetSerializer(BaseSendEmailResetSerializer, UserFunctionsMixin):
    default_error_messages = {
        "email_not_found": 'Email không tồn tại'
    }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_type', 'product_id', 'product_name', 'img', 'quantity', 'price', 'color', 'discount',
                  'place', 'product_line', 'cost_price']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'img']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'full_name', 'email', 'phone', 'shipping_address', 'status', 'payment_method',
                  'total_price']


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['order_id', 'product', 'price', 'quantity']


class UserEditSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Đã tồn tại email")])
    phone_number = serializers.CharField(max_length=254, validators=[
        UniqueValidator(queryset=user.objects.all(), message="Số điện thoại đã được sử dụng")])

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'is_active', 'address', 'birthday',
                  'gender']
