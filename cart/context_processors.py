from .cart import Cart


def cart(request):
    """Expose the number of cart items to every template (navbar badge)."""
    return {'cart_count': Cart(request).count}
