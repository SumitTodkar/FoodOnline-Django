from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.my_orders, name='list'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:order_number>/', views.order_success, name='success'),
    path('<str:order_number>/', views.order_detail, name='detail'),
    path('<str:order_number>/cancel/', views.cancel_order, name='cancel'),
]
