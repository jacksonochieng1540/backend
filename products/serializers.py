from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'is_active', 
                  'product_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'category_name', 'price', 
                  'compare_price', 'discount_percentage', 'stock', 'is_in_stock',
                  'image', 'is_featured', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'category_id', 'description',
                  'price', 'compare_price', 'discount_percentage', 'stock', 
                  'is_in_stock', 'sku', 'image', 'images', 'is_active', 
                  'is_featured', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'category', 'description', 'price', 'compare_price',
                  'stock', 'sku', 'image', 'is_active', 'is_featured')

    def validate(self, attrs):
        if attrs.get('compare_price') and attrs.get('price'):
            if attrs['compare_price'] < attrs['price']:
                raise serializers.ValidationError({
                    'compare_price': 'Compare price must be greater than or equal to price.'
                })
        return attrs