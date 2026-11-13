from django.conf import settings

from menu.models import Category


def site(request):
    """Values needed by the base template on every page."""
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_LOGO': settings.SITE_LOGO,
        'CURRENCY': settings.CURRENCY_SYMBOL,
        'DELIVERY_CHARGE': settings.DELIVERY_CHARGE,
        'FREE_DELIVERY_ABOVE': settings.FREE_DELIVERY_ABOVE,
        'nav_categories': Category.objects.filter(is_active=True),
    }
