# File: forms.py
# Author: Shuwei Zhu (david996@bu.edu), 6/25/2025
# Description: Django forms for the toilet app.
# Contains form classes for creating Restroom, Review, Order, and updating Stall occupancy.

from django import forms
from .models import Restroom, Review, Order, Stall, Product
from django.contrib.auth.forms import UserCreationForm
from .models import User


class CreateRestroomForm(forms.ModelForm):
    """Form for creating a new restroom.
    
    Uses Django's ModelForm to automatically generate form fields
    based on the Restroom model structure.
    """
    
    # additional field for number of stalls to create
    num_stalls = forms.IntegerField(
        min_value=1, 
        max_value=20,
        initial=3,
        help_text="Number of stalls in this restroom"
    )
    
    class Meta:
        """Meta class defines which model and fields to use for the form."""
        model = Restroom
        # specify which fields from the Restroom model should be included in the form
        fields = ['name', 'address']
        # created_by and timestamps are handled automatically in the view
        

class CreateReviewForm(forms.ModelForm):
    """Form for creating a new restroom review.
    
    Uses Django's ModelForm to generate form fields for review creation.
    Includes rating, comment, and photo upload functionality.
    """
    
    class Meta:
        """Associate this form with the Review model and select fields."""
        model = Review
        # include rating and comment fields - restroom and author handled in view
        fields = ['rating', 'comment_text', 'photo']
        # add custom widget for rating to use a select dropdown
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
            'comment_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'})
        }


class UpdateStallStatusForm(forms.ModelForm):
    """Form for updating stall occupancy status.
    
    Allows users to update whether a stall is occupied or not.
    """
    
    class Meta:
        """Associate this form with the Stall model."""
        model = Stall
        # only allow updating the occupancy status
        fields = ['is_occupied']
        # use a checkbox for boolean field
        widgets = {
            'is_occupied': forms.CheckboxInput()
        }


class CreateOrderForm(forms.Form):
    """Form for creating supply orders.
    
    Custom form for handling product orders with quantity selection.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize form with dynamic product choices."""
        super().__init__(*args, **kwargs)
        
        # get all available products with stock
        available_products = Product.objects.filter(stock_qty__gt=0)
        
        # create a field for each product
        for product in available_products:
            field_name = f'product_{product.id}'
            self.fields[field_name] = forms.IntegerField(
                min_value=0,
                max_value=product.stock_qty,
                initial=0,
                required=False,
                label=f'{product.name} (${product.unit_price})',
                help_text=f'{product.stock_qty} available'
            )
    
    def clean(self):
        """Validate that at least one product is selected."""
        cleaned_data = super().clean()
        
        # check if any product has quantity > 0
        has_items = any(
            value and value > 0 
            for key, value in cleaned_data.items() 
            if key.startswith('product_')
        )
        
        if not has_items:
            raise forms.ValidationError("Please select at least one product to order.")
        
        return cleaned_data


class SearchRestroomForm(forms.Form):
    """Form for searching restrooms by location or name.
    
    Simple search form with text input for finding restrooms.
    """
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name or address...',
            'class': 'search-input'
        })
    )
    
    # rating filter
    min_rating = forms.ChoiceField(
        choices=[('', 'Any Rating')] + [(i, f'{i}+ Stars') for i in range(1, 6)],
        required=False
    )
    
    # occupancy filter
    has_available_stalls = forms.BooleanField(
        required=False,
        label='Show only restrooms with available stalls'
    )
    
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'avatar_url', 'default_delivery_address', 'password1', 'password2')