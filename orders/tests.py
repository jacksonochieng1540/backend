from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order

User = get_user_model()


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='UserPass123!',
            first_name='Test',
            last_name='User'
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            description='Test description',
            price=50.00,
            stock=10
        )
        
        # Create cart with items
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        self.client.force_authenticate(user=self.user)

    def test_create_order(self):
        """Test creating an order from cart"""
        url = reverse('orders:order-list')
        data = {
            'shipping_address': '123 Test St',
            'shipping_city': 'Test City',
            'shipping_state': 'Test State',
            'shipping_country': 'Test Country',
            'shipping_postal_code': '12345',
            'phone_number': '1234567890'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user).exists())

    def test_list_user_orders(self):
        """Test listing user's orders"""
        Order.objects.create(
            user=self.user,
            shipping_address='123 Test St',
            shipping_city='Test City',
            shipping_state='Test State',
            shipping_country='Test Country',
            shipping_postal_code='12345',
            phone_number='1234567890',
            subtotal=100.00,
            total=120.00
        )
        
        url = reverse('orders:order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

