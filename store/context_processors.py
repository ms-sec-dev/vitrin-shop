import django
from django.conf import settings

from .cart import Cart
from .models import Category


def cart(request):
    current_cart = Cart(request)
    return {
        "cart": current_cart,
        "cart_count": len(current_cart),
        "cart_total": current_cart.total,
        "nav_categories": Category.objects.all(),
        "FREE_SHIPPING_THRESHOLD": settings.FREE_SHIPPING_THRESHOLD,
        "SHIPPING_PRICE": settings.SHIPPING_PRICE,
        "django_version": django.get_version(),
    }
