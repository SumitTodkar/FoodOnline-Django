from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from .utils import unique_slugify


class Category(models.Model):

    name = models.CharField(max_length=80, unique=True)

    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )

    description = models.CharField(
        max_length=200,
        blank=True
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True
    )

    is_active = models.BooleanField(default=True)

    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu:category', args=[self.slug])
    


class Restaurant(models.Model):

    name = models.CharField(max_length=120, unique=True)

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True
    )

    cuisine = models.CharField(max_length=120)

    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='restaurants/',
        blank=True
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=Decimal('4.0'),
        validators=[
            MinValueValidator(Decimal('0')),
            MaxValueValidator(Decimal('5')),
        ],
    )

    delivery_time = models.PositiveSmallIntegerField(default=30)

    is_featured = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(
                self,
                self.name,
                max_length=140
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('menu:list')}?restaurant={self.slug}"
    


class Food(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='foods'
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='foods'
    )

    name = models.CharField(max_length=120)

    slug = models.SlugField(
        max_length=140,
        unique=True,
        blank=True
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'))
        ],
    )

    image = models.ImageField(
        upload_to='foods/',
        blank=True
    )

    is_available = models.BooleanField(default=True)

    is_veg = models.BooleanField(
        default=True,
        verbose_name='vegetarian'
    )

    is_popular = models.BooleanField(default=False)

    preparation_time = models.PositiveSmallIntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(
                self,
                self.name,
                max_length=140
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu:detail', args=[self.slug])