from django.shortcuts import render

from menu.models import Category, Food, Restaurant

from .models import Banner, Offer, Testimonial


def home(request):
    popular_foods = list(
        Food.objects.filter(is_popular=True, is_available=True, category__is_active=True)
        .select_related('category', 'restaurant')[:8]
    )
    context = {
        'categories': Category.objects.filter(is_active=True),
        'popular_foods': popular_foods,
        'hero_foods': [food for food in popular_foods if food.image][:3],
        'restaurants': Restaurant.objects.filter(is_featured=True, is_active=True)[:6],
        'offers': Offer.objects.filter(is_active=True).select_related('category')[:4],
        'banners': Banner.objects.filter(is_active=True)[:3],
        'testimonials': Testimonial.objects.filter(is_active=True)[:6],
    }
    return render(request, 'core/home.html', context)
