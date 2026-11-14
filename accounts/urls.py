from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),

    path('login/', views.CustomLoginView.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('profile/', views.profile, name='profile'),

    path(
        'change-password/',
        views.ChangePasswordView.as_view(),
        name='password_change'
    ),

    path('addresses/', views.address_list, name='address_list'),

    path('addresses/add/', views.address_create, name='address_create'),

    path(
        'addresses/<int:pk>/edit/',
        views.address_update,
        name='address_update'
    ),

    path(
        'addresses/<int:pk>/delete/',
        views.address_delete,
        name='address_delete'
    ),

    path(
        'addresses/<int:pk>/default/',
        views.address_set_default,
        name='address_set_default'
    ),
]
