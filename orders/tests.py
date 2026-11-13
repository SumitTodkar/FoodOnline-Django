from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Address
from menu.models import Category, Food

from .models import Order

User = get_user_model()

ADDRESS_DATA = {
    'address': '',
    'full_name': 'Asha Verma',
    'phone': '9876543210',
    'email': 'asha@example.com',
    'address_line1': '12 MG Road',
    'address_line2': '',
    'landmark': 'Near the park',
    'city': 'Mumbai',
    'state': 'Maharashtra',
    'pincode': '400001',
    'notes': '',
    'payment_method': 'cod',
}


@override_settings(DELIVERY_CHARGE=Decimal('40.00'), FREE_DELIVERY_ABOVE=Decimal('500.00'))
class OrderFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('asha', 'asha@example.com', 'StrongPass#123', first_name='Asha')
        cls.other = User.objects.create_user('ravi', 'ravi@example.com', 'StrongPass#123')
        category = Category.objects.create(name='Biryani')
        cls.food = Food.objects.create(
            category=category, name='Veg Biryani', description='Tasty', price=Decimal('229.00'),
        )

    def _fill_cart(self, quantity=2):
        self.client.post(reverse('cart:add', args=[self.food.pk]), {'quantity': quantity})

    def test_checkout_requires_login(self):
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_empty_cart_redirects_to_menu(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('orders:checkout'))
        self.assertRedirects(response, reverse('menu:list'))

    def test_checkout_creates_order_with_server_side_totals(self):
        self.client.force_login(self.user)
        self._fill_cart(2)  # 458 + 40 delivery
        response = self.client.post(reverse('orders:checkout'), ADDRESS_DATA)
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse('orders:success', args=[order.order_number]))
        self.assertEqual(order.subtotal, Decimal('458.00'))
        self.assertEqual(order.delivery_charge, Decimal('40.00'))
        self.assertEqual(order.total, Decimal('498.00'))
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.payment_method, 'cod')
        item = order.items.get()
        self.assertEqual((item.name, item.quantity, item.price), ('Veg Biryani', 2, Decimal('229.00')))
        self.assertEqual(self.client.session.get('cart', {}), {})

    def test_price_changes_after_order_do_not_alter_history(self):
        self.client.force_login(self.user)
        self._fill_cart(1)
        self.client.post(reverse('orders:checkout'), ADDRESS_DATA)
        Food.objects.filter(pk=self.food.pk).update(price=Decimal('999.00'))
        item = Order.objects.get(user=self.user).items.get()
        self.assertEqual(item.price, Decimal('229.00'))

    def test_new_address_fields_are_required_without_saved_address(self):
        self.client.force_login(self.user)
        self._fill_cart()
        data = dict(ADDRESS_DATA, city='', pincode='')
        response = self.client.post(reverse('orders:checkout'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertIn('city', response.context['form'].errors)

    def test_invalid_pincode_rejected(self):
        self.client.force_login(self.user)
        self._fill_cart()
        response = self.client.post(reverse('orders:checkout'), dict(ADDRESS_DATA, pincode='12'))
        self.assertFalse(Order.objects.exists())
        self.assertIn('pincode', response.context['form'].errors)

    def test_saved_address_can_be_used(self):
        address = Address.objects.create(
            user=self.user, full_name='Asha Verma', phone='9876543210', line1='5 Park Street',
            city='Pune', state='Maharashtra', pincode='411001',
        )
        self.client.force_login(self.user)
        self._fill_cart()
        data = {'address': address.pk, 'payment_method': 'cod'}
        self.client.post(reverse('orders:checkout'), data)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.city, 'Pune')
        self.assertEqual(order.address_line1, '5 Park Street')

    def test_cannot_use_another_customers_address(self):
        foreign = Address.objects.create(
            user=self.other, full_name='Ravi', phone='9123456789', line1='9 Lake Road',
            city='Delhi', state='Delhi', pincode='110001',
        )
        self.client.force_login(self.user)
        self._fill_cart()
        self.client.post(reverse('orders:checkout'), {'address': foreign.pk, 'payment_method': 'cod'})
        self.assertFalse(Order.objects.exists())

    def test_unsupported_payment_method_rejected(self):
        self.client.force_login(self.user)
        self._fill_cart()
        self.client.post(reverse('orders:checkout'), dict(ADDRESS_DATA, payment_method='bitcoin'))
        self.assertFalse(Order.objects.exists())

    def test_customer_cannot_view_someone_elses_order(self):
        self.client.force_login(self.user)
        self._fill_cart()
        self.client.post(reverse('orders:checkout'), ADDRESS_DATA)
        order = Order.objects.get(user=self.user)

        self.client.force_login(self.other)
        self.assertEqual(self.client.get(order.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.post(reverse('orders:cancel', args=[order.order_number])).status_code, 404)

    def test_pending_order_can_be_cancelled_but_confirmed_cannot(self):
        self.client.force_login(self.user)
        self._fill_cart()
        self.client.post(reverse('orders:checkout'), ADDRESS_DATA)
        order = Order.objects.get(user=self.user)
        self.client.post(reverse('orders:cancel', args=[order.order_number]))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)

        order.status = Order.Status.CONFIRMED
        order.save()
        self.client.post(reverse('orders:cancel', args=[order.order_number]))
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CONFIRMED)

    def test_cod_order_marked_paid_when_delivered(self):
        self.client.force_login(self.user)
        self._fill_cart()
        self.client.post(reverse('orders:checkout'), ADDRESS_DATA)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PENDING)
        order.status = Order.Status.DELIVERED
        order.save()
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)

    def test_my_orders_lists_only_own_orders(self):
        self.client.force_login(self.user)
        self._fill_cart()
        self.client.post(reverse('orders:checkout'), ADDRESS_DATA)
        self.client.force_login(self.other)
        response = self.client.get(reverse('orders:list'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_tracking_steps_progress(self):
        order = Order(status=Order.Status.PREPARING)
        states = [step['state'] for step in order.tracking_steps]
        self.assertEqual(states, ['done', 'done', 'current', 'upcoming', 'upcoming'])
        self.assertEqual(Order(status=Order.Status.CANCELLED).tracking_steps, [])
