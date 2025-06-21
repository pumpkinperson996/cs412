# project/serializers.py

from rest_framework import serializers
from .models import Restroom, Stall, Review, Product, Order, User


class UserSerializer(serializers.ModelSerializer):
    """User info serializer"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar_url', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'avatar_url']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        if 'avatar_url' in validated_data:
            user.avatar_url = validated_data['avatar_url']
            user.save()
        return user


class StallSerializer(serializers.ModelSerializer):
    """Stall serializer"""
    class Meta:
        model = Stall
        fields = ['id', 'restroom', 'stall_no', 'is_occupied', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class RestroomSerializer(serializers.ModelSerializer):
    """Restroom serializer"""
    created_by = UserSerializer(read_only=True)
    stall_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Restroom
        fields = ['id', 'name', 'address', 'created_by', 'avg_rating', 
                  'created_at', 'stall_count']
        read_only_fields = ['id', 'created_at', 'avg_rating']
    
    def get_stall_count(self, obj):
        return obj.stalls.count()


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer"""
    author = UserSerializer(read_only=True)
    restroom_name = serializers.CharField(source='restroom.name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'restroom', 'restroom_name', 'author', 'rating', 
                  'comment_text', 'photo_urls', 'created_at']
        read_only_fields = ['id', 'created_at', 'restroom_name']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1-5")
        return value


class ProductSerializer(serializers.ModelSerializer):
    """Product serializer"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'unit_price', 'stock_qty', 'image_url']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""
    buyer = UserSerializer(read_only=True)
    restroom_name = serializers.CharField(source='restroom.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'buyer', 'restroom', 'restroom_name', 'items', 
                  'total_amount', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'restroom_name']
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must contain at least one item")
        return value