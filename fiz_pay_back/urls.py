from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/v1/auth/', include('djoser.urls.authtoken')),
    path('api/v1/auth/', include('djoser.urls')),
    path('payments/', include('payments.urls')),
    path('api/v1/', include('paymentcert.urls')),
    path('api/v1/', include('payments.urls')),
]
