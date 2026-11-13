from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Banner(models.Model):
    """Promotional food banner shown on the homepage."""

    title = models.CharField(max_length=80)
    subtitle = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True)
    button_text = models.CharField(max_length=30, default='Order now')
    button_url = models.CharField(
        max_length=200, default='/menu/',
        help_text='Site path such as /menu/category/pizza/ or a full https:// link.',
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.title


class Offer(models.Model):
    """A special offer displayed on the homepage (informational promotion)."""

    title = models.CharField(max_length=80)
    description = models.CharField(max_length=200)
    badge = models.CharField(max_length=30, blank=True, help_text='Short label such as "Free delivery".')
    category = models.ForeignKey(
        'menu.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='offers',
        help_text='Optional: the offer links to this category.',
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.title

    @property
    def link(self):
        if self.category_id:
            return self.category.get_absolute_url()
        return reverse('menu:list')


class Testimonial(models.Model):
    """A customer testimonial shown on the homepage."""

    name = models.CharField(max_length=80)
    location = models.CharField(max_length=80, blank=True)
    text = models.TextField(max_length=400)
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.rating}/5)'
