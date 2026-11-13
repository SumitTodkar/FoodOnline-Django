from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Address, Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('label', 'full_name', 'phone', 'line1', 'city', 'state', 'pincode', 'is_default')


admin.site.unregister(User)


@admin.register(User)
class CustomerAdmin(DjangoUserAdmin):
    """Django's user admin, extended with phone number and saved addresses."""

    inlines = (ProfileInline, AddressInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_select_related = ('profile',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone')

    @admin.display(description='Phone', ordering='profile__phone')
    def phone(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone if profile else ''


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'full_name', 'phone', 'city', 'pincode', 'is_default')
    list_filter = ('label', 'is_default', 'state')
    search_fields = ('user__username', 'full_name', 'phone', 'city', 'pincode')
    list_select_related = ('user',)
