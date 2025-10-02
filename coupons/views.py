from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Coupon, CouponUsage
from .serializers import (
    CouponSerializer,
    CouponValidateSerializer,
    CouponUsageSerializer
)


class CouponViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Coupon CRUD operations
    """
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    lookup_field = 'code'

    def get_permissions(self):
        if self.action in ['validate', 'apply']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ['list', 'retrieve'] and not self.request.user.is_staff:
            now = timezone.now()
            return Coupon.objects.filter(
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            )
        return Coupon.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def validate(self, request):
        """Validate a coupon code"""
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code'].upper()
        order_total = serializer.validated_data['order_total']
        
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({
                'error': 'Invalid coupon code'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if coupon is valid
        is_valid, message = coupon.is_valid()
        if not is_valid:
            return Response({
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check minimum purchase amount
        if order_total < coupon.min_purchase_amount:
            return Response({
                'error': f'Minimum purchase amount is ${coupon.min_purchase_amount}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check user usage limit
        user_usage_count = CouponUsage.objects.filter(
            coupon=coupon,
            user=request.user
        ).count()
        
        if user_usage_count >= coupon.usage_limit_per_user:
            return Response({
                'error': 'You have already used this coupon the maximum number of times'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        discount_amount = coupon.calculate_discount(order_total)
        
        return Response({
            'valid': True,
            'coupon': CouponSerializer(coupon).data,
            'discount_amount': discount_amount,
            'final_total': order_total - discount_amount
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, code=None):
        """Deactivate a coupon"""
        coupon = self.get_object()
        coupon.is_active = False
        coupon.save()
        
        return Response({
            'message': f'Coupon {coupon.code} has been deactivated',
            'coupon': CouponSerializer(coupon).data
        })


class CouponUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Coupon Usage history
    """
    serializer_class = CouponUsageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CouponUsage.objects.all().select_related('coupon', 'user', 'order')
        return CouponUsage.objects.filter(user=user).select_related('coupon', 'order')

