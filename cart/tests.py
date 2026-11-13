from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from menu.models import Category, Food


@override_settings(DELIVERY_CHARGE=Decimal('40.00'), FREE_DELIVERY_ABOVE=Decimal('500.00'))
class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Pizza')
        cls.cheap = Food.objects.create(
            category=cls.category, name='Margherita', description='Classic', price=Decimal('200.00'),
        )
        cls.pricey = Food.objects.create(
            category=cls.category, name='Farmhouse', description='Loaded', price=Decimal('350.00'),
        )
        cls.unavailable = Food.objects.create(
            category=cls.category, name='Sold Out Pizza', description='Gone', price=Decimal('100.00'),
            is_available=False,
        )

    def test_add_and_quantity_changes(self):
        self.client.post(reverse('cart:add', args=[self.cheap.pk]), {'quantity': 2})
        self.client.post(reverse('cart:increase', args=[self.cheap.pk]))
        self.assertEqual(self.client.session['cart'], {str(self.cheap.pk): 3})
        self.client.post(reverse('cart:decrease', args=[self.cheap.pk]))
        self.assertEqual(self.client.session['cart'], {str(self.cheap.pk): 2})

    def test_decreasing_to_zero_removes_item(self):
        self.client.post(reverse('cart:add', args=[self.cheap.pk]))
        self.client.post(reverse('cart:decrease', args=[self.cheap.pk]))
        self.assertEqual(self.client.session['cart'], {})

    def test_remove_item(self):
        self.client.post(reverse('cart:add', args=[self.cheap.pk]))
        self.client.post(reverse('cart:remove', args=[self.cheap.pk]))
        self.assertEqual(self.client.session['cart'], {})

    def test_cannot_add_unavailable_food(self):
        self.client.post(reverse('cart:add', args=[self.unavailable.pk]))
        self.assertNotIn(str(self.unavailable.pk), self.client.session.get('cart', {}))

    def test_totals_with_delivery_charge(self):
        self.client.post(reverse('cart:add', args=[self.cheap.pk]), {'quantity': 2})  # 400
        response = self.client.get(reverse('cart:detail'))
        cart = response.context['cart']
        self.assertEqual(cart.subtotal, Decimal('400.00'))
        self.assertEqual(cart.delivery_charge, Decimal('40.00'))
        self.assertEqual(cart.total, Decimal('440.00'))
        self.assertEqual(cart.free_delivery_gap, Decimal('100.00'))

    def test_free_delivery_over_threshold(self):
        self.client.post(reverse('cart:add', args=[self.pricey.pk]), {'quantity': 2})  # 700
        cart = self.client.get(reverse('cart:detail')).context['cart']
        self.assertEqual(cart.delivery_charge, Decimal('0.00'))
        self.assertEqual(cart.total, Decimal('700.00'))

    def test_ajax_add_returns_json_count(self):
        response = self.client.post(
            reverse('cart:add', args=[self.cheap.pk]), {'quantity': 3},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)

    def test_quantity_is_capped(self):
        self.client.post(reverse('cart:add', args=[self.cheap.pk]), {'quantity': 999})
        self.assertEqual(self.client.session['cart'][str(self.cheap.pk)], 20)

    def test_add_requires_post(self):
        response = self.client.get(reverse('cart:add', args=[self.cheap.pk]))
        self.assertEqual(response.status_code, 405)
