from django.contrib import admin
from .models import User, Restroom, Stall, Review, Product, Order

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')

@admin.register(Restroom)
class RestroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_by', 'avg_rating', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('created_at',)

@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = ('restroom', 'stall_no', 'is_occupied', 'updated_at')
    list_filter = ('is_occupied',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restroom', 'author', 'rating', 'created_at')
    search_fields = ('comment_text',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_price', 'stock_qty')
    search_fields = ('name',)
    list_filter = ('stock_qty',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'restroom', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('buyer__username',)
