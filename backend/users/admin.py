from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'id', 'email', 'first_name', 'last_name',)
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
