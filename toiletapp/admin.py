# File: admin.py
# Author: Shuwei Zhu (david996@bu.edu), 6/25/2025
# Description: Django admin configuration for the toilet app.
# Registers models with the Django admin interface for easy management
# and provides custom admin views with enhanced functionality.

from django.contrib import admin

# import our custom models to register them with the admin interface
from .models import User, Restroom, Stall, Review, Product, Order


# custom admin class for User model with enhanced display
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model with custom display and search."""
    
    # fields to display in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    
    # fields that can be searched
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # fields to filter by in the sidebar
    list_filter = ('is_active', 'is_staff', 'date_joined')
    
    # default ordering
    ordering = ('-date_joined',)


# custom admin class for Restroom model
@admin.register(Restroom)
class RestroomAdmin(admin.ModelAdmin):
    """Admin interface for Restroom model with custom display and filtering."""
    
    # fields to display in the list view
    list_display = ('name', 'address', 'created_by', 'avg_rating', 'stall_count', 'created_at')
    
    # fields that can be searched
    search_fields = ('name', 'address', 'created_by__username')
    
    # fields to filter by
    list_filter = ('avg_rating', 'created_at')
    
    # make avg_rating read-only since it's calculated
    readonly_fields = ('avg_rating', 'created_at')
    
    # default ordering
    ordering = ('-created_at',)
    
    def stall_count(self, obj):
        """Display the number of stalls for each restroom."""
        return obj.stalls.count()
    
    # give the column a nice header
    stall_count.short_description = 'Number of Stalls'


# inline admin for stalls to be edited within restroom admin
class StallInline(admin.TabularInline):
    """Inline admin to edit stalls directly from restroom admin page."""
    
    model = Stall
    # number of empty forms to show
    extra = 1
    # fields to display
    fields = ('stall_no', 'is_occupied', 'updated_at')
    # make updated_at read-only
    readonly_fields = ('updated_at',)


# update restroom admin to include inline stalls
class RestroomWithStallsAdmin(admin.ModelAdmin):
    """Enhanced Restroom admin with inline stall editing."""
    
    # all the previous RestroomAdmin settings
    list_display = ('name', 'address', 'created_by', 'avg_rating', 'stall_count', 'created_at')
    search_fields = ('name', 'address', 'created_by__username')
    list_filter = ('avg_rating', 'created_at')
    readonly_fields = ('avg_rating', 'created_at')
    ordering = ('-created_at',)
    
    # add the inline
    inlines = [StallInline]
    
    def stall_count(self, obj):
        """Display the number of stalls for each restroom."""
        return obj.stalls.count()
    
    stall_count.short_description = 'Number of Stalls'


# unregister the previous registration and re-register with new admin
admin.site.unregister(Restroom)
admin.site.register(Restroom, RestroomWithStallsAdmin)


# custom admin class for Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model with enhanced display."""
    
    # fields to display in the list view
    list_display = ('restroom', 'author', 'rating', 'comment_preview', 'created_at')
    
    # fields that can be searched
    search_fields = ('restroom__name', 'author__username', 'comment_text')
    
    # fields to filter by
    list_filter = ('rating', 'created_at')
    
    # default ordering
    ordering = ('-created_at',)
    
    # make created_at read-only
    readonly_fields = ('created_at',)
    
    def comment_preview(self, obj):
        """Show first 50 characters of comment in list view."""
        return obj.comment_text[:50] + '...' if len(obj.comment_text) > 50 else obj.comment_text
    
    comment_preview.short_description = 'Comment Preview'


# custom admin class for Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model with inventory management."""
    
    # fields to display in the list view
    list_display = ('name', 'unit_price', 'stock_qty', 'in_stock', 'description_preview')
    
    # fields that can be searched
    search_fields = ('name', 'description')
    
    # fields to filter by
    list_filter = ('stock_qty',)
    
    # default ordering
    ordering = ('name',)
    
    # editable fields in list view for quick updates
    list_editable = ('unit_price', 'stock_qty')
    
    def in_stock(self, obj):
        """Display whether product is in stock with boolean icon."""
        return obj.stock_qty > 0
    
    # display as boolean icon
    in_stock.boolean = True
    in_stock.short_description = 'In Stock'
    
    def description_preview(self, obj):
        """Show first 50 characters of description."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    
    description_preview.short_description = 'Description'


# custom admin class for Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model with order management features."""
    
    # fields to display in the list view
    list_display = ('id', 'buyer', 'restroom', 'total_amount', 'status', 'created_at')
    
    # fields that can be searched
    search_fields = ('buyer__username', 'restroom__name', 'id')
    
    # fields to filter by
    list_filter = ('status', 'created_at')
    
    # default ordering
    ordering = ('-created_at',)
    
    # make certain fields read-only
    readonly_fields = ('buyer', 'restroom', 'items', 'total_amount', 'created_at')
    
    # allow quick status updates from list view
    list_editable = ('status',)
    
    # custom display of order details
    fieldsets = (
        ('Order Information', {
            'fields': ('buyer', 'restroom', 'created_at')
        }),
        ('Order Details', {
            'fields': ('items', 'total_amount')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly except status for existing orders."""
        if obj:  # editing an existing object
            return self.readonly_fields
        return []


# register Stall model separately for direct management
@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    """Admin interface for individual stall management."""
    
    # fields to display in the list view
    list_display = ('restroom', 'stall_no', 'is_occupied', 'updated_at')
    
    # fields that can be searched
    search_fields = ('restroom__name',)
    
    # fields to filter by
    list_filter = ('is_occupied', 'updated_at')
    
    # allow quick occupancy updates from list view
    list_editable = ('is_occupied',)
    
    # default ordering
    ordering = ('restroom', 'stall_no')