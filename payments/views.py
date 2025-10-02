from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction
from .models import Payment
from .serializers import (
    PaymentSerializer,
    PaymentIntentSerializer,
    PaymentConfirmSerializer
)
from .stripe_handler import StripePaymentHandler
from orders.models import Order


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payment operations
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all().select_related('order', 'user')
        return Payment.objects.filter(user=user).select_related('order')

    @action(detail=False, methods=['post'])
    def create_intent(self, request):
        """Create payment intent"""
        serializer = PaymentIntentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        payment_method = serializer.validated_data['payment_method']
        
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            payment_method=payment_method,
            amount=order.total,
            status='pending'
        )
        
        # Handle different payment methods
        if payment_method == 'stripe':
            result = StripePaymentHandler.create_payment_intent(order, request.user)
            
            if result['success']:
                payment.payment_intent_id = result['payment_intent_id']
                payment.status = 'processing'
                payment.save()
                
                return Response({
                    'payment_id': payment.id,
                    'client_secret': result['client_secret'],
                    'payment_intent_id': result['payment_intent_id']
                }, status=status.HTTP_201_CREATED)
            else:
                payment.status = 'failed'
                payment.error_message = result['error']
                payment.save()
                
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add other payment methods (PayPal, Razorpay) here
        return Response({
            'error': 'Payment method not implemented'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """Confirm payment"""
        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        try:
            payment = Payment.objects.get(
                payment_intent_id=payment_intent_id,
                user=request.user
            )
        except Payment.DoesNotExist:
            return Response({
                'error': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify payment with Stripe
        result = StripePaymentHandler.confirm_payment(payment_intent_id)
        
        if result['success'] and result['status'] == 'succeeded':
            with transaction.atomic():
                payment.status = 'completed'
                payment.transaction_id = payment_intent_id
                payment.completed_at = timezone.now()
                payment.save()
                
                # Update order
                order = payment.order
                order.is_paid = True
                order.paid_at = timezone.now()
                order.payment_method = payment.payment_method
                order.status = 'processing'
                order.save()
            
            return Response({
                'message': 'Payment confirmed successfully',
                'payment': PaymentSerializer(payment).data
            })
        else:
            payment.status = 'failed'
            payment.error_message = result.get('error', 'Payment failed')
            payment.save()
            
            return Response({
                'error': result.get('error', 'Payment failed')
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Refund a payment"""
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response({
                'error': 'Can only refund completed payments'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if payment.payment_method == 'stripe':
            result = StripePaymentHandler.create_refund(payment.payment_intent_id)
            
            if result['success']:
                payment.status = 'refunded'
                payment.save()
                
                return Response({
                    'message': 'Refund processed successfully',
                    'payment': PaymentSerializer(payment).data
                })
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Refund not supported for this payment method'
        }, status=status.HTTP_400_BAD_REQUEST)


