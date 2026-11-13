from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Address, Profile
from cart.cart import Cart

from .forms import CheckoutForm
from .models import Order, OrderItem
from .payments import get_payment_handler


@transaction.atomic
def _create_order(request, cart, form):
    """Turn the session cart into an order. Totals are computed server-side."""
    data = form.cleaned_data
    order = Order.objects.create(
        user=request.user,
        full_name=data['full_name'],
        phone=data['phone'],
        email=data.get('email') or request.user.email,
        address_line1=data['address_line1'],
        address_line2=data.get('address_line2', ''),
        landmark=data.get('landmark', ''),
        city=data['city'],
        state=data['state'],
        pincode=data['pincode'],
        notes=data.get('notes', ''),
        payment_method=data['payment_method'],
        subtotal=cart.subtotal,
        delivery_charge=cart.delivery_charge,
        total=cart.total,
    )
    OrderItem.objects.bulk_create([
        OrderItem(order=order, food=item['food'], name=item['food'].name,
                  price=item['price'], quantity=item['quantity'])
        for item in cart.items
    ])

    redirect_url = get_payment_handler(order.payment_method).initiate(order)
    order.save()

    if data.get('save_address') and not data.get('address'):
        Address.objects.create(
            user=request.user, label='Home', full_name=data['full_name'], phone=data['phone'],
            line1=data['address_line1'], line2=data.get('address_line2', ''),
            landmark=data.get('landmark', ''), city=data['city'], state=data['state'],
            pincode=data['pincode'],
        )
    return order, redirect_url


@login_required
def checkout(request):
    cart = Cart(request)
    if cart.count == 0:
        messages.info(request, 'Your cart is empty. Add something tasty first!')
        return redirect('menu:list')
    if cart.has_unavailable:
        messages.warning(request, 'Some items in your cart are no longer available. Please remove them to continue.')
        return redirect('cart:detail')

    if request.method == 'POST':
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():
            order, redirect_url = _create_order(request, cart, form)
            cart.clear()
            messages.success(request, f'Order {order.order_number} placed successfully!')
            if redirect_url:  # future online payment gateways
                return redirect(redirect_url)
            return redirect('orders:success', order_number=order.order_number)
        messages.error(request, 'Please correct the errors below.')
    else:
        profile = Profile.objects.filter(user=request.user).first()
        default_address = request.user.addresses.filter(is_default=True).first()
        form = CheckoutForm(request.user, initial={
            'address': default_address.pk if default_address else None,
            'full_name': request.user.get_full_name(),
            'phone': profile.phone if profile else '',
            'email': request.user.email,
            'payment_method': Order.PaymentMethod.COD,
        })
    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


def _get_own_order(request, order_number):
    """Fetch an order that belongs to the logged-in customer, or raise 404."""
    return get_object_or_404(
        Order.objects.prefetch_related('items'), order_number=order_number, user=request.user,
    )


@login_required
def order_success(request, order_number):
    return render(request, 'orders/order_success.html', {'order': _get_own_order(request, order_number)})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    status = request.GET.get('status', '')
    if status in Order.Status.values:
        orders = orders.filter(status=status)
    else:
        status = ''
    page_obj = Paginator(orders, 8).get_page(request.GET.get('page'))
    return render(request, 'orders/my_orders.html', {
        'page_obj': page_obj,
        'status': status,
        'status_choices': Order.Status.choices,
    })


@login_required
def order_detail(request, order_number):
    return render(request, 'orders/order_detail.html', {'order': _get_own_order(request, order_number)})


@login_required
@require_POST
def cancel_order(request, order_number):
    order = _get_own_order(request, order_number)
    if not order.can_cancel:
        messages.error(request, 'This order can no longer be cancelled because it is already being processed.')
    else:
        order.status = Order.Status.CANCELLED
        order.save()
        messages.success(request, f'Order {order.order_number} has been cancelled.')
    return redirect('orders:detail', order_number=order.order_number)
