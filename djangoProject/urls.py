"""
URL configuration for LittleMon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from converse.views import CustomTokenObtainPairView, ProductViewSet, inventory_add, inventory_edit, page_gender, \
    detail_product, banner, check_out, get_order, order_detail, change_status, get_customers, edit_customers, \
    calculate_revenue_and_profit_by_year, calculate_total_revenue_and_profit_for_years
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('product', ProductViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('restaurant/', include('converse.urls')),
    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='custom_jwt_create'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path("", include(router.urls)),
    path('page/', page_gender),
    path("shoes/<int:id>", detail_product),
    path("banner/", banner),
    path("inventory/", inventory_add, name="inventory"),
    path("inventory/<int:id>", inventory_edit, name="inventory_edit"),
    path("checkout/", check_out),
    path("order/", get_order),
    path("order_detail/<slug:id>", order_detail, name="order_detail"),
    path("change_status/<slug:id>", change_status, name="change_status"),
    path("customer/", get_customers),
    path("customer_edit/<slug:id>", edit_customers, name="edit_customers"),
    path("profit_by_year/", calculate_revenue_and_profit_by_year, name="calculate_revenue_and_profit_by_year"),
    path("profit_for_years/", calculate_total_revenue_and_profit_for_years,
         name="calculate_total_revenue_and_profit_for_years"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
