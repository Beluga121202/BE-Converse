from django.conf import settings
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
from django.core.paginator import EmptyPage, Paginator
from .models import Product
from .serializers import CustomTokenObtainPairSerializer, UserCreateSerializer, ProductSerializer

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


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]


@api_view(["POST"])
@permission_classes([AllowAny])
def inventory_add(request):
    if request.method == 'POST':
        product_type = request.data.get('product_type')
        product_id = request.data.get('product_id')
        if Product.objects.filter(product_id=product_id).exists():
            error_message = {'error': 'Mã sản phẩm đã tồn tại'}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        product_name = request.data.get('product_name')
        img = request.data.get('img')
        quantity = request.data.get('quantity')
        price = request.data.get('price')
        discount = request.data.get('discount')
        place = request.data.get('place')
        product_line = request.data.get('product_line')
        Product.objects.create(product_type=product_type, product_id=product_id, product_name=product_name, img=img,
                               quantity=quantity, price=price, discount=discount, place=place,
                               product_line=product_line)
        return HttpResponse("Success", status=status.HTTP_201_CREATED)


@api_view(["PUT", "POST"])
@permission_classes([AllowAny])
def inventory_edit(request, id):
    try:
        item = Product.objects.get(pk=id)
    except Product.DoesNotExist():
        return Response({'error': 'Mã sản phẩm đã tồn tại'}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PUT':
        serializer = ProductSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        item.delete()
        return Response({'success': 'Xoá thành công'}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def page_gender(request):
    if request.method == "GET":
        data = Product.objects.all()
        category_name = request.query_params.get("product_type")
        to_price = request.query_params.getlist("to_price")
        product_line = request.query_params.getlist("product_line")
        print(product_line)
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=50)
        page = request.query_params.get("page", default=1)
        if category_name:
            data = data.filter(product_type=category_name)
        if to_price:
            data = data.filter(price__range=to_price)
        if search:
            data = data.filter(product_name__startswith=search)
        if product_line:
            data = data.filter(product_line__in=product_line)
        if ordering:
            ordering_fields = ordering.split(",")
            data = data.order_by(*ordering_fields)

        paginator = Paginator(data, per_page=perpage)
        try:
            data = paginator.page(number=page)
        except EmptyPage:
            data = []
        serializer = ProductSerializer(data, many=True)
        for item in serializer.data:
            if 'img' in item:
                item['img'] = request.build_absolute_uri(item['img'])

        return Response(serializer.data, status=status.HTTP_200_OK)
