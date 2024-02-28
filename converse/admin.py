from django.contrib import admin
from .models import User, Product


# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active',
                    'is_deactivated', 'is_staff', 'is_superuser')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Product)