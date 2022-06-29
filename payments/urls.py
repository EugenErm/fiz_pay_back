from django.urls import path, include
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'payments', views.PaymentsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('balance/', views.BalanceAPIView.as_view()),
]
