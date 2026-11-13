from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,13}$',
    message='Enter a valid phone number: 10 to 13 digits, with an optional leading +.',
)

pincode_validator = RegexValidator(
    regex=r'^\d{6}$',
    message='Enter a valid 6-digit PIN code.',
)


class Profile(models.Model):
    """Extra customer details that do not belong on Django's User model."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, validators=[phone_validator])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user}'


class Address(models.Model):
    """A saved delivery address belonging to a customer."""

    LABEL_CHOICES = [('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=20, choices=LABEL_CHOICES, default='Home')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    line1 = models.CharField('address line 1', max_length=200)
    line2 = models.CharField('address line 2', max_length=200, blank=True)
    landmark = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    pincode = models.CharField('PIN code', max_length=6, validators=[pincode_validator])
    is_default = models.BooleanField(default=False, verbose_name='default address')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f'{self.label}: {self.full_name}, {self.city} {self.pincode}'

    def save(self, *args, **kwargs):
        # A customer's first address automatically becomes the default.
        if not self.pk and not Address.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)

    @property
    def full_address(self):
        parts = [self.line1, self.line2, self.landmark, self.city, self.state, self.pincode]
        return ', '.join(part for part in parts if part)
