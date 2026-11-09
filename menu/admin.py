from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Restaurant, Food


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'is_active',
        'display_order',
    )

    list_filter = ('is_active',)

    search_fields = ('name',)

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'cuisine',
        'rating',
        'delivery_time',
        'is_featured',
        'is_active',
    )

    list_filter = (
        'cuisine',
        'is_featured',
        'is_active',
    )

    search_fields = ('name', 'cuisine')

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'restaurant',
        'price',
        'is_veg',
        'is_available',
        'is_popular',
    )

    list_filter = (
        'category',
        'restaurant',
        'is_veg',
        'is_available',
        'is_popular',
    )

    search_fields = ('name', 'description')

    prepopulated_fields = {
        'slug': ('name',)
    }