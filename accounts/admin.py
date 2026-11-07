from django.contrib import admin
from .models import Profile, Address


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'phone',
        'created_at',
    )

    search_fields = (
        'user__username',
        'phone',
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'user',
        'label',
        'city',
        'pincode',
        'is_default',
    )

    list_filter = (
        'label',
        'city',
        'is_default',
    )

    search_fields = (
        'full_name',
        'phone',
        'city',
        'pincode',
    )