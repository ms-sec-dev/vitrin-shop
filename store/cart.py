from django.conf import settings

from .models import Product

CART_SESSION_ID = "cart"


def shipping_cost(subtotal: int) -> int:
    if subtotal <= 0 or subtotal >= settings.FREE_SHIPPING_THRESHOLD:
        return 0
    return settings.SHIPPING_PRICE


class Cart:
    """Session-backed shopping cart. Works without login, ideal for a demo."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not isinstance(cart, dict):
            cart = {}
        self.cart = cart

    def save(self):
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def add(self, product: Product, quantity: int = 1, override: bool = False):
        key = str(product.pk)
        current = self.cart.get(key, {}).get("quantity", 0)
        quantity = max(0, int(quantity))
        new_quantity = quantity if override else current + quantity
        new_quantity = min(new_quantity, product.stock)
        if new_quantity > 0:
            self.cart[key] = {"quantity": new_quantity}
        else:
            self.cart.pop(key, None)
        self.save()

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)
        self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def __iter__(self):
        ids = [int(key) for key in self.cart.keys() if str(key).isdigit()]
        products = Product.objects.filter(pk__in=ids, is_active=True).select_related("category")
        product_map = {str(product.pk): product for product in products}
        for key, item in list(self.cart.items()):
            product = product_map.get(key)
            if product is None:
                continue
            quantity = min(item.get("quantity", 0), product.stock)
            if quantity <= 0:
                continue
            yield {
                "product": product,
                "quantity": quantity,
                "subtotal": product.price * quantity,
            }

    def __len__(self):
        return sum(item.get("quantity", 0) for item in self.cart.values())

    @property
    def total(self) -> int:
        return sum(row["subtotal"] for row in self)

    @property
    def shipping(self) -> int:
        return shipping_cost(self.total)

    @property
    def payable(self) -> int:
        return self.total + self.shipping

    @property
    def free_shipping_remaining(self) -> int:
        return max(0, settings.FREE_SHIPPING_THRESHOLD - self.total)

    @property
    def free_shipping_progress(self) -> int:
        if settings.FREE_SHIPPING_THRESHOLD <= 0:
            return 100
        return min(100, round(self.total * 100 / settings.FREE_SHIPPING_THRESHOLD))

    @property
    def total_quantity(self) -> int:
        return len(self)

    def __bool__(self):
        return bool(self.cart)
