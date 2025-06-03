# File: forms.py
# Author: Shuwei Zhu (david996@bu.edu), 6/3/2025
# Description: Django forms for the mini_fb application.
# Contains form classes for creating Profile and StatusMessage objects.

from django import forms
from .models import Profile, StatusMessage


class CreateProfileForm(forms.ModelForm):
    """Form for creating a new user profile.
    
    Uses Django's ModelForm to automatically generate form fields
    based on the Profile model structure.
    """
    
    class Meta:
        """Meta class defines which model and fields to use for the form."""
        model = Profile
        # specify which fields from the Profile model should be included in the form
        fields = ['first_name', 'last_name', 'city', 'email_address', 'image_url']
        
        
class CreateStatusMessageForm(forms.ModelForm):
    """Form for creating a new status message.
    
    Uses Django's ModelForm to generate form fields for status message creation.
    """
    
    class Meta:
        """Associate this form with the StatusMessage model and select fields."""
        model = StatusMessage
        # only include the message field - profile and timestamp are handled automatically
        fields = ['message']