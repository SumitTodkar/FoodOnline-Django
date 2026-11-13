from django.urls import path

from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='list'),
    path('category/<slug:category_slug>/', views.menu_list, name='category'),
    path('food/<slug:slug>/', views.food_detail, name='detail'),
]
