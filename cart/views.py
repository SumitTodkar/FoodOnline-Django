from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from menu.models import Food

from .cart import Cart


def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _safe_next(request):
    target = request.POST.get('next', '')
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return target
    return reverse('cart:detail')


def _respond(request, cart, message, level='success'):
    """JSON for the JavaScript add-to-cart buttons, a redirect for plain forms."""
    if _is_ajax(request):
        ok = level != 'error'
        return JsonResponse(
            {'ok': ok, 'level': level, 'message': message, 'count': cart.count},
            status=200 if ok else 400,
        )
    getattr(messages, level)(request, message)
    return redirect(_safe_next(request))


def _parse_quantity(request):
    try:
        quantity = int(request.POST.get('quantity', '1'))
    except (TypeError, ValueError):
        quantity = 1
    return max(1, min(quantity, settings.CART_MAX_QUANTITY))


def cart_detail(request):
    return render(request, 'cart/cart.html', {'cart': Cart(request)})


@require_POST
def add_to_cart(request, food_id):
    cart = Cart(request)
    food = Food.objects.select_related('category').filter(pk=food_id).first()
    if food is None:
        return _respond(request, cart, 'That dish could not be found.', 'error')
    if not (food.is_available and food.category.is_active):
        return _respond(request, cart, f'Sorry, {food.name} is currently unavailable.', 'error')

    before = cart.quantity_of(food.pk)
    cart.add(food, _parse_quantity(request))
    if cart.quantity_of(food.pk) == before:
        return _respond(
            request, cart,
            f'You already have the maximum of {settings.CART_MAX_QUANTITY} x {food.name}.', 'warning',
        )
    return _respond(request, cart, f'{food.name} added to your cart.')


@require_POST
def increase_item(request, food_id):
    cart = Cart(request)
    food = Food.objects.select_related('category').filter(pk=food_id).first()
    if food is None or not (food.is_available and food.category.is_active):
        return _respond(request, cart, 'This item is no longer available.', 'error')
    before = cart.quantity_of(food.pk)
    cart.increase(food)
    if cart.quantity_of(food.pk) == before:
        return _respond(request, cart, f'Maximum quantity of {settings.CART_MAX_QUANTITY} reached.', 'warning')
    return redirect(_safe_next(request))


@require_POST
def decrease_item(request, food_id):
    cart = Cart(request)
    cart.decrease(food_id)
    return redirect(_safe_next(request))


@require_POST
def remove_item(request, food_id):
    cart = Cart(request)
    cart.remove(food_id)
    messages.info(request, 'Item removed from your cart.')
    return redirect(_safe_next(request))
