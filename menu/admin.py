from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Category, Food, Restaurant


def _thumbnail(obj):
    if obj.image:
        return format_html(
            '<img src="{}" alt="" style="height:44px;width:60px;object-fit:cover;border-radius:6px;">',
            obj.image.url,
        )
    return '—'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'display_order', 'is_active', 'food_count')
    list_display_links = ('thumbnail', 'name')
    list_editable = ('display_order', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(foods_total=Count('foods'))

    @admin.display(description='Image')
    def thumbnail(self, obj):
        return _thumbnail(obj)

    @admin.display(description='Foods', ordering='foods_total')
    def food_count(self, obj):
        return obj.foods_total


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'cuisine', 'rating', 'delivery_time', 'is_featured', 'is_active')
    list_display_links = ('thumbnail', 'name')
    list_editable = ('is_featured', 'is_active')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('name', 'cuisine')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Image')
    def thumbnail(self, obj):
        return _thumbnail(obj)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail', 'name', 'category', 'restaurant', 'price',
        'is_available', 'is_popular', 'is_veg', 'preparation_time',
    )
    list_display_links = ('thumbnail', 'name')
    list_editable = ('price', 'is_available', 'is_popular')
    list_filter = ('category', 'restaurant', 'is_available', 'is_veg', 'is_popular')
    list_select_related = ('category', 'restaurant')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    actions = ('mark_available', 'mark_unavailable')
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'restaurant', 'description')}),
        ('Pricing and availability', {'fields': ('price', 'is_available', 'preparation_time')}),
        ('Presentation', {'fields': ('image', 'is_veg', 'is_popular')}),
    )

    @admin.display(description='Image')
    def thumbnail(self, obj):
        return _thumbnail(obj)

    @admin.action(description='Mark selected foods as available')
    def mark_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} food item(s) marked as available.')

    @admin.action(description='Mark selected foods as unavailable')
    def mark_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} food item(s) marked as unavailable.')
