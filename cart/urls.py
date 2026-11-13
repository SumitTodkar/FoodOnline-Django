from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/<int:food_id>/', views.add_to_cart, name='add'),
    path('increase/<int:food_id>/', views.increase_item, name='increase'),
    path('decrease/<int:food_id>/', views.decrease_item, name='decrease'),
    path('remove/<int:food_id>/', views.remove_item, name='remove'),
]
