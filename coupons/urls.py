from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, CouponUsageViewSet

app_name = 'coupons'

router = DefaultRouter()
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'usage', CouponUsageViewSet, basename='coupon-usage')

urlpatterns = [
    path('', include(router.urls)),
]