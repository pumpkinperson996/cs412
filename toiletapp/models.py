# File: models.py
# Author: Shuwei Zhu (david996@bu.edu), 6/25/2025
# Description: Django models for the toilet app.
# Defines the data models for restrooms, reviews, orders, and related entities
# with enhanced functionality for the public restroom finder application.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone


class User(AbstractUser):
    """Custom user model with optional avatar support and additional fields.
    
    Extends Django's AbstractUser to add profile-specific fields
    for the toilet app users.
    """
    
    # optional avatar URL for user profile pictures
    avatar_url = models.URLField(blank=True)
    
    # track user's favorite restrooms for quick access
    favorite_restrooms = models.ManyToManyField(
        'Restroom', 
        related_name='favorited_by', 
        blank=True
    )
    
    # user's default delivery address for supply orders
    default_delivery_address = models.CharField(max_length=300, blank=True)

    def __str__(self):
        """Return username as string representation."""
        return self.username
    
    def get_recent_reviews(self, limit=5):
        """Return user's most recent reviews.
        
        Args:
            limit: Maximum number of reviews to return
            
        Returns:
            QuerySet of Review objects ordered by creation date
        """
        return self.review_set.order_by('-created_at')[:limit]


class Restroom(models.Model):
    """Model representing a public restroom location.
    
    Contains location information, ratings, and relationships
    to stalls and reviews.
    """
    
    # basic restroom information
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    
    # optional fields for enhanced location features
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Latitude for map display"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Longitude for map display"
    )
    
    # accessibility information
    is_accessible = models.BooleanField(
        default=False,
        help_text="Wheelchair accessible"
    )
    has_baby_changing = models.BooleanField(
        default=False,
        help_text="Has baby changing station"
    )
    
    # metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    avg_rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return restroom name as string representation."""
        return self.name
    
    def get_absolute_url(self):
        """Return the URL to display this restroom's detail page."""
        return reverse('toiletapp:show_restroom', kwargs={'pk': self.pk})
    
    def get_available_stalls_count(self):
        """Return the number of currently available stalls."""
        return self.stalls.filter(is_occupied=False).count()
    
    def get_total_stalls_count(self):
        """Return the total number of stalls."""
        return self.stalls.count()
    
    def get_occupancy_percentage(self):
        """Calculate and return the occupancy percentage."""
        total = self.get_total_stalls_count()
        if total == 0:
            return 0
        occupied = self.stalls.filter(is_occupied=True).count()
        return round((occupied / total) * 100, 1)
    
    def update_average_rating(self):
        """Recalculate and save the average rating based on all reviews."""
        from django.db.models import Avg
        
        avg = self.review_set.aggregate(Avg('rating'))['rating__avg']
        self.avg_rating = avg if avg else 0
        self.save()
    
    class Meta:
        """Meta options for the Restroom model."""
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['avg_rating']),
        ]


class Stall(models.Model):
    """Model representing individual stalls within a restroom.
    
    Tracks occupancy status and provides real-time availability info.
    """
    
    # relationship to parent restroom
    restroom = models.ForeignKey(
        Restroom, 
        related_name="stalls", 
        on_delete=models.CASCADE
    )
    
    # stall identification and status
    stall_no = models.IntegerField(validators=[MinValueValidator(1)])
    is_occupied = models.BooleanField(default=False)
    
    # track when status was last updated
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who last updated the status"
    )

    def __str__(self):
        """Return formatted stall identifier."""
        return f"{self.restroom.name} - Stall {self.stall_no}"
    
    def get_time_since_update(self):
        """Return human-readable time since last update."""
        return timezone.now() - self.updated_at
    
    def toggle_occupancy(self, user=None):
        """Toggle the occupancy status and track who updated it."""
        self.is_occupied = not self.is_occupied
        self.updated_by = user
        self.save()
    
    class Meta:
        """Meta options for the Stall model."""
        ordering = ['stall_no']
        unique_together = ['restroom', 'stall_no']


class Review(models.Model):
    """Model representing user reviews for restrooms.
    
    Includes ratings, comments, and optional photo uploads.
    """
    
    # core review fields
    restroom = models.ForeignKey(Restroom, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment_text = models.TextField()
    
    # store URLs of uploaded photos as JSON list
    photo_urls = models.JSONField(
        default=list,
        blank=True,
        help_text="List of photo URLs"
    )
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True)

    
    # metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # track if review was verified (user actually visited)
    is_verified = models.BooleanField(
        default=False,
        help_text="Review from verified visit"
    )

    def __str__(self):
        """Return formatted review summary."""
        return f"Review by {self.author.username} on {self.restroom.name}"
    
    def get_absolute_url(self):
        """Return URL to the restroom this review belongs to."""
        return self.restroom.get_absolute_url()
    
    def save(self, *args, **kwargs):
        """Override save to update restroom rating after saving."""
        super().save(*args, **kwargs)
        # update the restroom's average rating
        self.restroom.update_average_rating()
    
    class Meta:
        """Meta options for the Review model."""
        ordering = ['-created_at']
        # prevent duplicate reviews from same user for same restroom
        unique_together = ['restroom', 'author']


class Product(models.Model):
    """Model representing products available for order.
    
    Tracks inventory and pricing for supplies like toilet paper.
    """
    
    # product categories
    CATEGORY_CHOICES = [
        ('paper', 'Toilet Paper'),
        ('sanitizer', 'Hand Sanitizer'),
        ('soap', 'Hand Soap'),
        ('towels', 'Paper Towels'),
        ('other', 'Other Supplies'),
    ]
    
    # product information
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='other'
    )
    
    # pricing and inventory
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock_qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # product image
    image_url = models.URLField()
    
    # track if product is currently available for order
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """Return product name as string representation."""
        return self.name
    
    def is_in_stock(self):
        """Check if product is currently in stock."""
        return self.stock_qty > 0
    
    def reduce_stock(self, quantity):
        """Reduce stock by specified quantity if available.
        
        Args:
            quantity: Amount to reduce stock by
            
        Returns:
            bool: True if stock was reduced, False if insufficient stock
        """
        if self.stock_qty >= quantity:
            self.stock_qty -= quantity
            self.save()
            return True
        return False
    
    class Meta:
        """Meta options for the Product model."""
        ordering = ['category', 'name']


class Order(models.Model):
    """Model representing supply orders placed by users.
    
    Tracks order details, delivery information, and status.
    """
    
    # order status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # order relationships
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    restroom = models.ForeignKey(
        Restroom, 
        on_delete=models.CASCADE,
        help_text="Delivery location"
    )
    
    # order details stored as JSON: {product_id: quantity}
    items = models.JSONField()
    
    # financial information
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # order status and tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default="pending"
    )
    tracking_number = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Shipping tracking number"
    )
    
    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Estimated delivery date/time"
    )
    
    # delivery notes
    delivery_notes = models.TextField(
        blank=True,
        help_text="Special delivery instructions"
    )

    def __str__(self):
        """Return formatted order identifier."""
        return f"Order #{self.id} by {self.buyer.username}"
    
    def get_absolute_url(self):
        """Return URL to order detail page."""
        return reverse('toiletapp:order_detail', kwargs={'pk': self.pk})
    
    def get_items_detail(self):
        """Return detailed information about ordered items.
        
        Returns:
            list: List of dictionaries with product details and quantities
        """
        items_detail = []
        for product_id, quantity in self.items.items():
            try:
                product = Product.objects.get(pk=int(product_id))
                items_detail.append({
                    'product': product,
                    'quantity': quantity,
                    'subtotal': product.unit_price * quantity
                })
            except Product.DoesNotExist:
                continue
        return items_detail
    
    def can_be_cancelled(self):
        """Check if order can still be cancelled."""
        return self.status in ['pending', 'confirmed']
    
    def cancel_order(self):
        """Cancel the order and restore product stock."""
        if self.can_be_cancelled():
            # restore stock for all items
            for product_id, quantity in self.items.items():
                try:
                    product = Product.objects.get(pk=int(product_id))
                    product.stock_qty += quantity
                    product.save()
                except Product.DoesNotExist:
                    continue
            
            # update order status
            self.status = 'cancelled'
            self.save()
            return True
        return False
    
    class Meta:
        """Meta options for the Order model."""
        ordering = ['-created_at']