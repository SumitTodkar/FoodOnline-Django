from decimal import Decimal

from django.conf import settings

from menu.models import Food

ZERO = Decimal('0.00')


class Cart:
    """
    Session-based shopping cart.

    The session only stores ``{food_id: quantity}``. Prices and availability
    are always read from the database, so a customer can never tamper with
    prices and admin changes are reflected immediately.
    """

    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID, {})
        self._items = None

    # -- persistence ---------------------------------------------------------
    def _save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
        self._items = None

    # -- modifying the cart ----------------------------------------------------
    def quantity_of(self, food_id):
        return int(self.cart.get(str(food_id), 0))

    def add(self, food, quantity=1):
        key = str(food.pk)
        self.cart[key] = min(self.quantity_of(food.pk) + quantity, settings.CART_MAX_QUANTITY)
        self._save()

    def increase(self, food):
        self.add(food, 1)

    def decrease(self, food_id):
        key = str(food_id)
        if key not in self.cart:
            return
        if self.cart[key] > 1:
            self.cart[key] -= 1
        else:
            del self.cart[key]
        self._save()

    def remove(self, food_id):
        if self.cart.pop(str(food_id), None) is not None:
            self._save()

    def clear(self):
        self.cart = {}
        self._save()

    # -- reading the cart ------------------------------------------------------
    @property
    def items(self):
        """List of dicts: food, quantity, price, total, available."""
        if self._items is None:
            foods = Food.objects.select_related('category', 'restaurant').in_bulk(
                [int(key) for key in self.cart]
            )
            items = []
            stale = []
            for key, quantity in self.cart.items():
                food = foods.get(int(key))
                if food is None:  # the dish was deleted by an admin
                    stale.append(key)
                    continue
                quantity = max(1, int(quantity))
                items.append({
                    'food': food,
                    'quantity': quantity,
                    'price': food.price,
                    'total': food.price * quantity,
                    'available': food.is_available and food.category.is_active,
                })
            if stale:
                for key in stale:
                    del self.cart[key]
                self._save()
            self._items = items
        return self._items

    def __iter__(self):
        return iter(self.items)

    @property
    def count(self):
        """Total number of individual items (sum of quantities)."""
        return sum(int(quantity) for quantity in self.cart.values())

    def __len__(self):
        return self.count

    @property
    def has_unavailable(self):
        return any(not item['available'] for item in self.items)

    @property
    def subtotal(self):
        return sum((item['total'] for item in self.items if item['available']), ZERO)

    @property
    def delivery_charge(self):
        subtotal = self.subtotal
        if subtotal <= 0 or subtotal >= settings.FREE_DELIVERY_ABOVE:
            return ZERO
        return settings.DELIVERY_CHARGE

    @property
    def total(self):
        return self.subtotal + self.delivery_charge

    @property
    def free_delivery_gap(self):
        """Amount still needed to qualify for free delivery (0 when qualified)."""
        subtotal = self.subtotal
        if subtotal <= 0:
            return ZERO
        return max(settings.FREE_DELIVERY_ABOVE - subtotal, ZERO)

    @property
    def free_delivery_progress(self):
        """Percentage (0-100) towards free delivery, for the progress bar."""
        threshold = settings.FREE_DELIVERY_ABOVE
        if threshold <= 0:
            return 100
        return int(min(self.subtotal / threshold * 100, 100))
