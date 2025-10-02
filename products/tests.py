
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()


class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='UserPass123!',
            first_name='Regular',
            last_name='User'
        )
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            description='Test description',
            price=99.99,
            stock=10,
            sku='TEST-001'
        )

    def test_list_products(self):
        """Test listing products (public access)"""
        url = reverse('products:product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_product(self):
        """Test retrieving a single product"""
        url = reverse('products:product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_create_product_as_admin(self):
        """Test creating product as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('products:product-list')
        data = {
            'name': 'New Product',
            'category': self.category.id,
            'description': 'New product description',
            'price': 149.99,
            'stock': 20,
            'sku': 'NEW-001'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_as_regular_user(self):
        """Test creating product as regular user (should fail)"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('products:product-list')
        data = {
            'name': 'New Product',
            'category': self.category.id,
            'description': 'New product description',
            'price': 149.99,
            'stock': 20,
            'sku': 'NEW-001'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
