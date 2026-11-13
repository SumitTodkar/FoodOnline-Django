"""Root URL configuration for the FoodOnline project."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'FoodOnline Administration'
admin.site.site_title = 'FoodOnline Admin'
admin.site.index_title = 'Manage your food ordering platform'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('menu/', include('menu.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('', include('core.urls')),
]

# Serve uploaded images (food photos etc.) during development only.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
