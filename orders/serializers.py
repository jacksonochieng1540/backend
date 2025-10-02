from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'total_price')
        read_only_fields = ('id', 'product_name', 'product_price', 'total_price')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user', 'user_email', 'status', 'status_display',
                  'shipping_address', 'shipping_city', 'shipping_state', 'shipping_country',
                  'shipping_postal_code', 'phone_number', 'subtotal', 'discount', 'tax',
                  'shipping_cost', 'total', 'is_paid', 'paid_at', 'payment_method',
                  'notes', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'order_number', 'user', 'subtotal', 'total', 
                           'is_paid', 'paid_at', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=500)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_country = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(max_length=15)
    notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not hasattr(user, 'cart') or not user.cart.items.exists():
            raise serializers.ValidationError("Cart is empty")
        return attrs


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

