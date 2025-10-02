# E-commerce Backend API

A complete Django REST Framework e-commerce backend with JWT authentication, product management, shopping cart, orders, payments, and coupons.

## Features

- 🔐 JWT Authentication (Registration, Login, Logout, Profile Management)
- 📦 Product Management (CRUD with categories, images, search, filters)
- 🛒 Shopping Cart (Add, Update, Remove items)
- 📋 Order Management (Create orders, track status, order history)
- 💳 Payment Integration (Stripe, PayPal, Razorpay support)
- 🎟️ Coupon & Discount System
- 🔍 Advanced Search & Filtering
- 📊 Admin Panel (Custom Django Admin)
- ⚡ Redis Caching for performance
- 📄 API Documentation (Swagger/OpenAPI)
- ✅ Unit Tests

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Caching**: Redis
- **Payment**: Stripe
- **Documentation**: drf-yasg (Swagger)
- **Image Processing**: Pillow

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd ecommerce_backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Setup PostgreSQL Database
```bash
# Create database
createdb ecommerce_db

# Or using psql
psql -U postgres
CREATE DATABASE ecommerce_db;
\q
```

### 6. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create superuser
```bash
python manage.py createsuperuser
```

### 8. Run development server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/accounts/register/` - Register new user
- `POST /api/accounts/login/` - Login user
- `POST /api/accounts/logout/` - Logout user
- `POST /api/accounts/token/refresh/` - Refresh JWT token
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile
- `POST /api/accounts/change-password/` - Change password

### Products
- `GET /api/products/` - List all products
- `GET /api/products/{slug}/` - Get product detail
- `POST /api/products/` - Create product (Admin only)
- `PUT /api/products/{slug}/` - Update product (Admin only)
- `DELETE /api/products/{slug}/` - Delete product (Admin only)
- `GET /api/products/featured/` - Get featured products

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{slug}/` - Get category detail
- `POST /api/categories/` - Create category (Admin only)

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/add_item/` - Add item to cart
- `PUT /api/cart/update_item/{item_id}/` - Update cart item
- `DELETE /api/cart/remove_item/{item_id}/` - Remove item from cart
- `DELETE /api/cart/clear/` - Clear cart

### Orders
- `GET /api/orders/` - List user's orders
- `GET /api/orders/{id}/` - Get order detail
- `POST /api/orders/` - Create order from cart
- `POST /api/orders/{id}/cancel/` - Cancel order
- `PATCH /api/orders/{id}/update_status/` - Update order status (Admin only)

### Payments
- `POST /api/payments/create_intent/` - Create payment intent
- `POST /api/payments/confirm/` - Confirm payment
- `POST /api/payments/{id}/refund/` - Refund payment

### Coupons
- `GET /api/coupons/` - List coupons (Admin only)
- `POST /api/coupons/` - Create coupon (Admin only)
- `POST /api/coupons/validate/` - Validate coupon code
- `POST /api/coupons/{code}/deactivate/` - Deactivate coupon (Admin only)

## Testing

Run tests:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test accounts
python manage.py test products
python manage.py test cart
python manage.py test orders
```

## API Documentation

Access interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Admin Panel

Access Django admin at: `http://localhost:8000/admin/`

## Redis Setup

Install Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Start Redis
redis-server
```

## Environment Variables

Required environment variables in `.env`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `STRIPE_SECRET_KEY` - Stripe secret key
- `REDIS_URL` - Redis connection URL

## Production Deployment

1. Set `DEBUG=False` in .env
2. Configure allowed hosts
3. Setup static files serving
4. Use production database
5. Setup Celery for async tasks
6. Configure email backend
7. Setup SSL certificates
8. Use gunicorn/uwsgi

## License

MIT License