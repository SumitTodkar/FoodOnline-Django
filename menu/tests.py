from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Category, Food


class MenuTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pizza = Category.objects.create(name='Pizza')
        cls.drinks = Category.objects.create(name='Beverages')
        cls.hidden = Category.objects.create(name='Hidden', is_active=False)
        cls.margherita = Food.objects.create(
            category=cls.pizza, name='Margherita', description='Cheesy classic', price=Decimal('249'), is_veg=True,
        )
        cls.pepperoni = Food.objects.create(
            category=cls.pizza, name='Pepperoni', description='Spicy chicken', price=Decimal('429'), is_veg=False,
        )
        cls.chai = Food.objects.create(
            category=cls.drinks, name='Masala Chai', description='Hot tea', price=Decimal('49'),
        )
        cls.secret = Food.objects.create(
            category=cls.hidden, name='Secret Dish', description='Hidden', price=Decimal('10'),
        )

    def names(self, response):
        return [food.name for food in response.context['page_obj']]

    def test_slugs_are_generated_and_unique(self):
        duplicate = Food.objects.create(category=self.pizza, name='Margherita', description='Again', price=Decimal('1'))
        self.assertEqual(self.margherita.slug, 'margherita')
        self.assertEqual(duplicate.slug, 'margherita-2')

    def test_menu_hides_inactive_categories(self):
        response = self.client.get(reverse('menu:list'))
        self.assertNotIn('Secret Dish', self.names(response))
        self.assertEqual(response.context['total_count'], 3)

    def test_category_filter(self):
        response = self.client.get(reverse('menu:category', args=[self.pizza.slug]))
        self.assertEqual(sorted(self.names(response)), ['Margherita', 'Pepperoni'])

    def test_unknown_or_inactive_category_is_404(self):
        self.assertEqual(self.client.get(reverse('menu:category', args=['nope'])).status_code, 404)
        self.assertEqual(self.client.get(reverse('menu:category', args=[self.hidden.slug])).status_code, 404)

    def test_search_matches_name_description_and_category(self):
        self.assertEqual(self.names(self.client.get(reverse('menu:list'), {'q': 'cheesy'})), ['Margherita'])
        self.assertEqual(self.names(self.client.get(reverse('menu:list'), {'q': 'beverages'})), ['Masala Chai'])

    def test_diet_filter_and_sorting(self):
        self.assertEqual(self.names(self.client.get(reverse('menu:list'), {'veg': '0'})), ['Pepperoni'])
        response = self.client.get(reverse('menu:list'), {'sort': 'price_high'})
        self.assertEqual(self.names(response), ['Pepperoni', 'Margherita', 'Masala Chai'])

    def test_available_only_filter(self):
        Food.objects.filter(pk=self.chai.pk).update(is_available=False)
        response = self.client.get(reverse('menu:list'), {'available': '1'})
        self.assertNotIn('Masala Chai', self.names(response))

    def test_food_detail_page(self):
        response = self.client.get(self.margherita.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Margherita')

    def test_food_in_inactive_category_is_404(self):
        self.assertEqual(self.client.get(self.secret.get_absolute_url()).status_code, 404)


class HomeAndSeedTests(TestCase):
    def test_home_page_renders_empty(self):
        self.assertEqual(self.client.get(reverse('core:home')).status_code, 200)

    def test_seed_data_command_is_idempotent(self):
        call_command('seed_data', '--skip-images', verbosity=0)
        food_count = Food.objects.count()
        call_command('seed_data', '--skip-images', verbosity=0)
        self.assertEqual(Food.objects.count(), food_count)
        self.assertEqual(Category.objects.count(), 7)
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Popular right now')
