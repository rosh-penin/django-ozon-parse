from django.urls import include, path
from rest_framework import routers

from .views import ProductsViewSet

router_v1 = routers.SimpleRouter()
router_v1.register('products', ProductsViewSet, basename='products')

urlpatterns = [
    path('', include(router_v1.urls))
]
