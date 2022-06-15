from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'paymentcert', views.PaymentCertViewSet)
urlpatterns = router.urls