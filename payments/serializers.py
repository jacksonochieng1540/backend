from rest_framework import serializers
from .models import Payment
from orders.models import Order

class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order', 'order_number', 'payment_method', 'amount', 'status',
                  'status_display', 'transaction_id', 'currency', 'created_at', 
                  'updated_at', 'completed_at')
        read_only_fields = ('id', 'user', 'amount', 'status', 'transaction_id', 
                           'created_at', 'updated_at', 'completed_at')


class PaymentIntentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)

    def validate_order_id(self, value):
        user = self.context['request'].user
        try:
            order = Order.objects.get(id=value, user=user)
            if order.is_paid:
                raise serializers.ValidationError("Order is already paid")
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        return value


class PaymentConfirmSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField()
