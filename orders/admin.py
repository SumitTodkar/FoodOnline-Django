from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'order_number',
        'user',
        'status',
        'payment_method',
        'payment_status',
        'total',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'payment_status',
    )

    search_fields = (
        'order_number',
        'full_name',
        'phone',
        'user__username',
    )

    readonly_fields = (
        'order_number',
        'created_at',
        'updated_at',
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'order',
        'name',
        'price',
        'quantity',
    )

    search_fields = ('name', 'order__order_number')