from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from carts.models import Cart
from decimal import Decimal 


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order operations
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().select_related('user').prefetch_related('items')
        return Order.objects.filter(user=user).select_related('user').prefetch_related('items')

    @transaction.atomic
    def create(self, request):
        """Create order from cart"""
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.select_related('product').all()
        
        if not cart_items:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate totals
        subtotal = sum(item.total_price for item in cart_items)
        discount = 0  
        tax = subtotal * Decimal('0.10')  # 10% tax
        shipping_cost = Decimal('10.00')  # Flat shipping
        total = subtotal - discount + tax + shipping_cost
        
        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=serializer.validated_data['shipping_address'],
            shipping_city=serializer.validated_data['shipping_city'],
            shipping_state=serializer.validated_data['shipping_state'],
            shipping_country=serializer.validated_data['shipping_country'],
            shipping_postal_code=serializer.validated_data['shipping_postal_code'],
            phone_number=serializer.validated_data['phone_number'],
            notes=serializer.validated_data.get('notes', ''),
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total
        )
        
        # Create order items
        for cart_item in cart_items:
            # Check stock availability
            if cart_item.quantity > cart_item.product.stock:
                order.delete()
                return Response({
                    'error': f'Insufficient stock for {cart_item.product.name}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
                total_price=cart_item.total_price
            )
            
            # Reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (Admin only)"""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order.status = serializer.validated_data['status']
        order.save()
        
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order"""
        order = self.get_object()
        
        if order.status in ['shipped', 'delivered']:
            return Response({
                'error': 'Cannot cancel order that has been shipped or delivered'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if order.is_paid:
            return Response({
                'error': 'Cannot cancel paid order. Please contact support for refund.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        
        order.status = 'cancelled'
        order.save()
        
        return Response(OrderSerializer(order).data)
