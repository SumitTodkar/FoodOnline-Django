from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = ('name', 'price', 'quantity', 'line_total')
    readonly_fields = ('name', 'price', 'quantity', 'line_total')

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Line total')
    def line_total(self, obj):
        return obj.line_total


def _status_action(status):
    label = Order.Status(status).label

    @admin.action(description=f'Mark selected orders as {label}')
    def action(modeladmin, request, queryset):
        # Saved one by one so Order.save() can update payment status for COD.
        count = 0
        for order in queryset:
            order.status = status
            order.save()
            count += 1
        modeladmin.message_user(request, f'{count} order(s) marked as {label}.')

    action.__name__ = f'mark_{status}'
    return action


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'full_name', 'phone', 'total', 'payment_method',
        'payment_status', 'status', 'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'email', 'user__username')
    date_hierarchy = 'created_at'
    list_select_related = ('user',)
    inlines = (OrderItemInline,)
    actions = [_status_action(value) for value in Order.Status.values]
    readonly_fields = (
        'order_number', 'user', 'subtotal', 'delivery_charge', 'total', 'created_at', 'updated_at',
    )
    fieldsets = (
        ('Order', {'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')}),
        ('Delivery details', {
            'fields': ('full_name', 'phone', 'email', 'address_line1', 'address_line2',
                       'landmark', 'city', 'state', 'pincode', 'notes'),
        }),
        ('Payment', {'fields': ('payment_method', 'payment_status', 'payment_reference')}),
        ('Amounts', {'fields': ('subtotal', 'delivery_charge', 'total')}),
    )

    def has_add_permission(self, request):
        # Orders are only created through the customer checkout.
        return False
