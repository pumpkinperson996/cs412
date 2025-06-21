# toiletapp/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom user model with optional avatar support
class User(AbstractUser):
    avatar_url = models.URLField(blank=True)

    def __str__(self):
        return self.username

# Basic restroom model
class Restroom(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    avg_rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Individual stall status within a restroom
class Stall(models.Model):
    restroom = models.ForeignKey(Restroom, related_name="stalls", on_delete=models.CASCADE)
    stall_no = models.IntegerField()
    is_occupied = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.restroom.name} - Stall {self.stall_no}"

# User reviews for restrooms
class Review(models.Model):
    restroom = models.ForeignKey(Restroom, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment_text = models.TextField()
    photo_urls = models.JSONField(default=list)  # List of image URLs
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.author.username} on {self.restroom.name}"

# Product model (e.g., toilet paper, sanitizer)
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_qty = models.IntegerField()
    image_url = models.URLField()

    def __str__(self):
        return self.name

# Order placed by a user
class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    restroom = models.ForeignKey(Restroom, on_delete=models.CASCADE)
    items = models.JSONField()  # Stores {product_id: quantity}
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"
