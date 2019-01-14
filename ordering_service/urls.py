from django.conf.urls import url, include
from rest_framework import routers
from ordering_service import views

router = routers.DefaultRouter()
router.register(r'orders', views.OrderViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
]
