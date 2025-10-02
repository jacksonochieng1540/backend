from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

app_name = 'carts'

router = DefaultRouter()
router.register(r'', CartViewSet, basename='carts')

urlpatterns = [
    path('', include(router.urls)),
]