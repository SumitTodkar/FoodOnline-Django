from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Category, Food, Restaurant

SORT_OPTIONS = {
    'popular': ('Most popular', ('-is_popular', 'name')),
    'price_low': ('Price: low to high', ('price', 'name')),
    'price_high': ('Price: high to low', ('-price', 'name')),
    'name': ('Name: A to Z', ('name',)),
}


def menu_list(request, category_slug=None):
    """Food listing with category, search, diet, availability and sort filters."""
    categories = Category.objects.filter(is_active=True)
    foods = Food.objects.filter(category__is_active=True).select_related('category', 'restaurant')

    active_category = None
    if category_slug:
        active_category = categories.filter(slug=category_slug).first()
        if active_category is None:
            raise Http404('Category not found.')
        foods = foods.filter(category=active_category)

    restaurant_slug = request.GET.get('restaurant', '').strip()
    active_restaurant = None
    if restaurant_slug:
        active_restaurant = Restaurant.objects.filter(slug=restaurant_slug, is_active=True).first()
        if active_restaurant:
            foods = foods.filter(restaurant=active_restaurant)

    query = request.GET.get('q', '').strip()
    if query:
        foods = foods.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(restaurant__name__icontains=query)
        )

    diet = request.GET.get('veg', '')
    if diet == '1':
        foods = foods.filter(is_veg=True)
    elif diet == '0':
        foods = foods.filter(is_veg=False)

    available_only = request.GET.get('available') == '1'
    if available_only:
        foods = foods.filter(is_available=True)

    sort = request.GET.get('sort', 'popular')
    if sort not in SORT_OPTIONS:
        sort = 'popular'
    foods = foods.order_by(*SORT_OPTIONS[sort][1])

    paginator = Paginator(foods, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    context = {
        'categories': categories,
        'active_category': active_category,
        'active_restaurant': active_restaurant,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'query': query,
        'diet': diet,
        'available_only': available_only,
        'sort': sort,
        'sort_options': [(key, label) for key, (label, _) in SORT_OPTIONS.items()],
        'querystring': params.urlencode(),
    }
    return render(request, 'menu/menu.html', context)


def food_detail(request, slug):
    food = get_object_or_404(
        Food.objects.select_related('category', 'restaurant'),
        slug=slug, category__is_active=True,
    )
    related = (
        Food.objects.filter(category=food.category, is_available=True, category__is_active=True)
        .exclude(pk=food.pk)
        .select_related('category', 'restaurant')[:4]
    )
    return render(request, 'menu/food_detail.html', {'food': food, 'related_foods': related})
