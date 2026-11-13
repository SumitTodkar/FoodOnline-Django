from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Address, Profile

User = get_user_model()

REGISTRATION_DATA = {
    'first_name': 'Asha',
    'last_name': 'Verma',
    'username': 'asha',
    'email': 'Asha@Example.com',
    'phone': '9876543210',
    'password1': 'Str0ng!Pass#2026',
    'password2': 'Str0ng!Pass#2026',
}


class AuthenticationTests(TestCase):
    def test_registration_creates_user_profile_and_logs_in(self):
        response = self.client.post(reverse('accounts:register'), REGISTRATION_DATA)
        self.assertRedirects(response, reverse('core:home'))
        user = User.objects.get(username='asha')
        self.assertEqual(user.email, 'asha@example.com')
        self.assertEqual(user.profile.phone, '9876543210')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_duplicate_email_rejected(self):
        User.objects.create_user('someone', 'asha@example.com', 'pass12345!')
        response = self.client.post(reverse('accounts:register'), REGISTRATION_DATA)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='asha').exists())
        self.assertIn('email', response.context['form'].errors)

    def test_login_and_logout(self):
        User.objects.create_user('asha', 'asha@example.com', 'Str0ng!Pass#2026')
        response = self.client.post(reverse('accounts:login'), {'username': 'asha', 'password': 'Str0ng!Pass#2026'})
        self.assertRedirects(response, reverse('core:home'))
        self.client.post(reverse('accounts:logout'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_does_not_redirect_to_external_site(self):
        User.objects.create_user('asha', 'asha@example.com', 'Str0ng!Pass#2026')
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'asha', 'password': 'Str0ng!Pass#2026', 'next': 'https://evil.example/'},
        )
        self.assertRedirects(response, reverse('core:home'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)


class ProfileAndAddressTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('asha', 'asha@example.com', 'Str0ng!Pass#2026')
        cls.other = User.objects.create_user('ravi', 'ravi@example.com', 'Str0ng!Pass#2026')

    def _address_data(self, **overrides):
        data = {
            'label': 'Home', 'full_name': 'Asha Verma', 'phone': '9876543210', 'line1': '12 MG Road',
            'line2': '', 'landmark': '', 'city': 'Mumbai', 'state': 'Maharashtra', 'pincode': '400001',
        }
        data.update(overrides)
        return data

    def test_profile_update(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'Asha', 'last_name': 'V', 'email': 'new@example.com', 'phone': '9123456780',
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertEqual(Profile.objects.get(user=self.user).phone, '9123456780')

    def test_change_password(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:password_change'), {
            'old_password': 'Str0ng!Pass#2026', 'new_password1': 'N3w!Passw0rd#77', 'new_password2': 'N3w!Passw0rd#77',
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3w!Passw0rd#77'))

    def test_first_address_becomes_default_and_default_is_unique(self):
        self.client.force_login(self.user)
        self.client.post(reverse('accounts:address_create'), self._address_data())
        self.client.post(reverse('accounts:address_create'), self._address_data(label='Work', city='Pune'))
        first, second = Address.objects.filter(user=self.user).order_by('id')
        self.assertTrue(first.is_default)
        self.assertFalse(second.is_default)

        self.client.post(reverse('accounts:address_set_default', args=[second.pk]))
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(second.is_default)

    def test_invalid_pincode_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:address_create'), self._address_data(pincode='abc'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Address.objects.exists())

    def test_cannot_edit_or_delete_another_users_address(self):
        address = Address.objects.create(
            user=self.other, full_name='Ravi', phone='9123456789', line1='9 Lake Road',
            city='Delhi', state='Delhi', pincode='110001',
        )
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('accounts:address_update', args=[address.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('accounts:address_delete', args=[address.pk])).status_code, 404)
        self.assertTrue(Address.objects.filter(pk=address.pk).exists())

    def test_deleting_default_promotes_another_address(self):
        self.client.force_login(self.user)
        self.client.post(reverse('accounts:address_create'), self._address_data())
        self.client.post(reverse('accounts:address_create'), self._address_data(label='Work'))
        default = Address.objects.get(user=self.user, is_default=True)
        self.client.post(reverse('accounts:address_delete', args=[default.pk]))
        self.assertTrue(Address.objects.get(user=self.user).is_default)
