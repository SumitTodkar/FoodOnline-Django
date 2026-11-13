
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from menu.models import Food
from .models import Cart, CartItem


@login_required
@require_POST
def add_to_cart(request, food_id):

    food = get_object_or_404(Food, pk=food_id)

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        food=food
    )

    # If the item already exists, increase quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(
        request,
        f"{food.name} added to your cart successfully!"
    )

    return redirect('cart:cart_detail')
