from django.urls import path

from . import views

urlpatterns = [
    path('', views.payments),
    path('<int:payment_id>/', views.get_payment_by_id),
    path('start/', views.start_payment_by_ids),
    path('balance/', views.get_balance),
    path('clear/', views.clear_payment_list),
    path('import/', views.upload_payment_list_file),
]