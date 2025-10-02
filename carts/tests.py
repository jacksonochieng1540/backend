from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Category, Product
from cart.models import Cart, CartItem

User = get_user_model()


class CartAPITestCase(APITestCase):
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
        
        self.client.force_authenticate(user=self.user)

    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        url = reverse('cart:cart-add-item')
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_items'], 2)

    def test_add_item_exceeds_stock(self):
        """Test adding more items than available stock"""
        url = reverse('cart:cart-add-item')
        data = {
            'product_id': self.product.id,
            'quantity': 20  # More than available stock
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        
        url = reverse('cart:cart-update-item', kwargs={'item_id': cart_item.id})
        data = {'quantity': 5}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_remove_cart_item(self):
        """Test removing item from cart"""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2
        )
        
        url = reverse('cart:cart-remove-item', kwargs={'item_id': cart_item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

