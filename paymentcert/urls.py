from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'paymentcert', views.PaymentCertViewSet, basename='user')
urlpatterns = router.urls

# urlpatterns = [
#     path('', views.PaymentCertAPIView.as_view({'get': 'list'})),
# ]