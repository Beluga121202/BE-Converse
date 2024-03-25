import uuid
import calendar
from datetime import datetime
from itertools import product

# Create your views here.
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.paginator import EmptyPage, Paginator
from .models import Product, Banner, OrderDetails, Order
from .serializers import CustomTokenObtainPairSerializer, ProductSerializer, BannerSerializer, OrderSerializer, \
    OrderDetailSerializer, UserEditSerializer
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

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
        img_base64 = request.data.get('img')  # Assuming img is in base64 format
        format, imgstr = img_base64.split(';base64,')
        ext = format.split('/')[-1]
        # Generate a unique filename
        file_name = str(uuid.uuid4()) + "." + ext  # Using UUID to ensure uniqueness
        # Decode base64 and save the image
        img_data = base64.b64decode(imgstr)
        fs = FileSystemStorage(location='media/images/')  # Define the storage location
        filename = fs.save(file_name, ContentFile(img_data))
        quantity = request.data.get('quantity')
        price = request.data.get('price')
        discount = request.data.get('discount')
        place = request.data.get('place')
        color = request.data.get('color')
        product_line = request.data.get('product_line')
        cost_price = request.data.get('cost_price')
        Product.objects.create(product_type=product_type, product_id=product_id, product_name=product_name,
                               img='images/' + file_name,
                               quantity=quantity, price=price, discount=discount, place=place,
                               product_line=product_line, color=color, cost_price=cost_price)
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
        category_name = request.query_params.getlist("product_type")
        to_price = request.query_params.getlist("to_price")
        gender = request.query_params.getlist("gender")
        product_line = request.query_params.getlist("product_line")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=50)
        page = request.query_params.get("page", default=1)
        if category_name:
            data = data.filter(product_type__in=category_name)
        if to_price:
            data = data.filter(price__range=to_price)

        if search:
            data = data.filter(product_name__startswith=search)
        if product_line:
            data = data.filter(product_line__in=product_line)
        if ordering:
            ordering_fields = ordering.split(",")
            print(ordering_fields)
            data = data.order_by(*ordering_fields)
            if category_name[0] == 'Sale':
                for item in data:
                    original_price = item.price
                    discount_percentage = item.discount
                    discounted_price = original_price * (1 - discount_percentage / 100)
                    item.discounted_price = discounted_price
                if ordering_fields[0] == 'price':
                    data = sorted(data, key=lambda x: x.discounted_price, reverse=False)
                else:
                    data = sorted(data, key=lambda x: x.discounted_price, reverse=True)
            else:
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


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def detail_product(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        data = serializer.data
        if 'img' in data:
            data['img'] = request.build_absolute_uri(data['img'])

        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def banner(request):
    if request.method == 'GET':
        title = request.query_params.get('title')
        data = Banner.objects.get(title=title)
        serializer = BannerSerializer(data)
        data_serializer = serializer.data
        if 'img' in data_serializer:
            data_serializer['img'] = request.build_absolute_uri(data_serializer['img'])
        return Response(data_serializer, status=status.HTTP_200_OK)
    if request.method == 'POST':
        img = request.data.get('img')
        title = request.data.get('title')
        Banner.objects.create(title=title, img=img)
        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def check_out(request):
    if request.method == 'POST':
        order_id = request.data.get('order_id')
        cart = request.data.get('cart')
        total_errors = []
        for item in cart:
            orders_product = Product.objects.get(product_id=item['product_id'])
            quantity_available = orders_product.quantity
            quantity_ordered = item['quantity']
            if quantity_ordered > quantity_available:
                total_errors.append(
                    f"Số lượng sản phẩm '{orders_product.product_name}' trong kho không đủ. Số lượng còn lại: {quantity_available}")

        if total_errors:
            return Response({'error': total_errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        for item in cart:
            OrderDetails.objects.create(
                order_id=order_id,
                price=item['product_price'] * (1 - item['discount'] / 100),
                quantity=item['quantity'],
                product=item['product_id'],
                cost_price=item['cost_price']
            )
            orders_product = Product.objects.get(product_id=item['product_id'])
            orders_product.quantity -= item['quantity']
            orders_product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_order(request):
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def order_detail(request, id):
    if request.method == 'POST':
        order = OrderDetails.objects.filter(order_id=id)
        serializer = OrderDetailSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def change_status(request, id):
    if request.method == 'POST':
        order = Order.objects.filter(order_id=id)
        data = request.data.get('status')
        order.update(status=data)
        return Response('Success', status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_customers(request):
    if request.method == 'GET':
        customers = User.objects.all()
        serializer = UserEditSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT", "POST"])
@permission_classes([AllowAny])
def edit_customers(request, id):
    if request.method == 'PUT':
        user = User.objects.filter(username=id).first()
        serializer = UserEditSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        user = User.objects.filter(username=id).first()
        user.delete()
        return Response({'success': 'Xoá thành công'}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def calculate_revenue_and_profit_by_year(request):
    if request.method == 'GET':
        year = datetime.now().year
        revenue_by_month = {}
        profit_by_month = {}

        for month in range(1, 13):
            orders = Order.objects.filter(
                status='Giao hàng thành công',
                created__year=year,
                created__month=month
            )
            total_revenue = 0
            total_profit = 0

            for order in orders:
                order_details = OrderDetails.objects.filter(order_id=order)
                for item in order_details:
                    total_revenue += item.price * item.quantity
                    total_profit += (item.price - item.cost_price) * item.quantity
            revenue_by_month[calendar.month_abbr[month]] = total_revenue
            profit_by_month[calendar.month_abbr[month]] = total_profit
        print(revenue_by_month)
        print(profit_by_month)
        return JsonResponse({'revenue_by_month': revenue_by_month, 'profit_by_month': profit_by_month},
                            status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def calculate_total_revenue_and_profit_for_years(request):
    if request.method == 'GET':
        current_year = datetime.now().year
        years_to_check = [current_year, current_year - 1, current_year - 2]
        result = {}

        for year in years_to_check:
            orders = Order.objects.filter(
                status='Giao hàng thành công',
                created__year=year
            )

            total_revenue = 0
            total_profit = 0

            for order in orders:
                order_details = OrderDetails.objects.filter(order_id=order)
                for item in order_details:
                    total_revenue += item.price * item.quantity
                    total_profit += (item.price - item.cost_price) * item.quantity

            result[year] = {'total_revenue': total_revenue, 'total_profit': total_profit}

        return JsonResponse(result, status=status.HTTP_200_OK)
