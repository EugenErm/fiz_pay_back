from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_payment_list),
    path('start/', views.start_payment_by_ids),
    path('clear/', views.clear_payment_list),
    path('import/', views.upload_payment_list_file),
]