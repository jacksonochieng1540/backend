from rest_framework import serializers
from .models import Coupon, CouponUsage
from django.utils import timezone

class CouponSerializer(serializers.ModelSerializer):
    is_valid_now = serializers.SerializerMethodField()
    discount_display = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ('id', 'code', 'description', 'discount_type', 'discount_value',
                  'min_purchase_amount', 'max_discount_amount', 'usage_limit',
                  'usage_limit_per_user', 'times_used', 'is_active', 'valid_from',
                  'valid_until', 'is_valid_now', 'discount_display', 'created_at')
        read_only_fields = ('id', 'times_used', 'created_at')

    def get_is_valid_now(self, obj):
        is_valid, _ = obj.is_valid()
        return is_valid

    def get_discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f"{obj.discount_value}%"
        return f"${obj.discount_value}"


class CouponValidateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value.upper())
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")
        
        is_valid, message = coupon.is_valid()
        if not is_valid:
            raise serializers.ValidationError(message)
        
        return value


class CouponUsageSerializer(serializers.ModelSerializer):
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CouponUsage
        fields = ('id', 'coupon', 'coupon_code', 'user_email', 'order',
                  'discount_amount', 'created_at')
        read_only_fields = ('id', 'created_at')

