from rest_framework.routers import SimpleRouter

from . import views


router = SimpleRouter()
router.register(r'payments', views.PaymentsViewSet)
urlpatterns = router.urls