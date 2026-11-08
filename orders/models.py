import secrets
import string

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PREPARING = 'preparing', 'Preparing'
        OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentMethod(models.TextChoices):
        COD = 'cod','Cash on Delivery'
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending','Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null = True,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    # Delivery information
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)

    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    landmark = models.CharField(max_length=120, blank=True)

    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    pincode = models.CharField(max_length=6)

    notes = models.CharField(
        'delivery instructions',
        max_length=300,
        blank=True
    )

    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True
    )

    # Price information
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    delivery_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_number}'

    def save(self, *args, **kwargs):

        if not self.order_number:
            self.order_number = self._generate_order_number()

        if (
            self.status == self.Status.DELIVERED
            and self.payment_method == self.PaymentMethod.COD
            and self.payment_status == self.PaymentStatus.PENDING
        ):
            self.payment_status = self.PaymentStatus.PAID

        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():

        alphabet = string.ascii_uppercase + string.digits

        while True:
            suffix = ''.join(
                secrets.choice(alphabet) for _ in range(5)
            )

            number = f"FO{timezone.now():%y%m%d}{suffix}"

            if not Order.objects.filter(order_number=number).exists():
                return number

    def get_absolute_url(self):
        return reverse('orders:detail', args=[self.order_number])

    @property
    def can_cancel(self):
        return self.status == self.Status.PENDING

    @property
    def is_cancelled(self):
        return self.status == self.Status.CANCELLED

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def full_address(self):

        parts = [
            self.address_line1,
            self.address_line2,
            self.landmark,
            self.city,
            self.state,
            self.pincode
        ]

        return ', '.join(part for part in parts if part)
    

    TRACKING_FLOW = (
    ('pending', 'Order placed', 'bi-hourglass-split'),
    ('confirmed', 'Confirmed', 'bi-check2-circle'),
    ('preparing', 'Preparing', 'bi-fire'),
    ('out_for_delivery', 'Out for delivery', 'bi-bicycle'),
    ('delivered', 'Delivered', 'bi-bag-check'),
    )
    
    BADGE_CLASSES = {
        'pending': 'warning text-dark',
        'confirmed': 'info text-dark',
        'preparing': 'primary',
        'out_for_delivery': 'dark',
        'delivered': 'success',
        'cancelled': 'danger',
    }

    @property
    def badge_class(self):
        return self.BADGE_CLASSES.get(self.status, 'secondary')


    @property
    def tracking_steps(self):

        if self.is_cancelled:
            return []

        values = [
            value for value, _, _ in self.TRACKING_FLOW
        ]

        current = values.index(self.status)

        steps = []

        for index, (value, label, icon) in enumerate(self.TRACKING_FLOW):

            if index < current or (
                index == current and value == 'delivered'
            ):
                state = 'done'

            elif index == current:
                state = 'current'

            else:
                state = 'upcoming'

            steps.append({
                'value': value,
                'label': label,
                'icon': icon,
                'state': state
            })

        return steps
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    food = models.ForeignKey(
        'menu.Food',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )

    name = models.CharField(max_length=120)

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.name}'
    
    @property
    def line_total(self):
        return self.price * self.quantity
