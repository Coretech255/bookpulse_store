from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/auth/', include('users.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('order/', include('orders.urls')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('', include('shop.urls')),
]

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
