from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Follow


class FoodgramUserAdmin(UserAdmin):
    model = FoodgramUser
    list_display = ('id', 'username', 'first_name', 'last_name',
                    'email', 'password', 'is_staff', 'is_active',)
    ordering = ('id',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)


admin.site.register(FoodgramUser,  FoodgramUserAdmin)
admin.site.register(Follow)