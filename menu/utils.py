from django.utils.text import slugify


def unique_slugify(instance, value, slug_field='slug', max_length=100):
    """Return a slug for ``value`` that is unique for the instance's model."""
    base = (slugify(value) or 'item')[: max_length - 6]
    slug = base
    model = instance.__class__
    counter = 2
    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f'{base}-{counter}'
        counter += 1
    return slug
