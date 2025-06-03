# File: models.py
# Author: Shuwei Zhu (david996@bu.edu), 6/3/2025
# Description: Django models for the mini_fb application.
# Defines the Profile and StatusMessage models with their fields and methods.

from django.db import models
from django.urls import reverse


class Profile(models.Model):
    """Model representing a user profile in the mini Facebook application.
    
    Contains personal information about a user including name, location,
    contact information, and profile image.
    """

    # user's first name - required field
    first_name = models.TextField(blank=False)
    
    # user's last name - required field
    last_name = models.TextField(blank=False)
    
    # user's city of residence - required field
    city = models.TextField(blank=False)
    
    # user's email address - required field
    email_address = models.TextField(blank=False)
    
    # URL to user's profile image - optional field
    image_url = models.URLField(blank=True)
    
    def __str__(self):
        """Return a string representation of this Profile object."""
        return f'{self.first_name} {self.last_name}'
    
    def get_all_StatusMessage(self):
        """Return all StatusMessage objects associated with this profile.
        
        Uses Django's ORM to filter StatusMessage objects by this profile
        as the foreign key relationship.
        """
        # filter all status messages that belong to this profile
        all_status_messages = StatusMessage.objects.filter(profile=self)
        return all_status_messages
    
    def get_absolute_url(self):
        """Return the URL to display this profile's detail page.
        
        Uses Django's reverse function to generate the URL based on
        the URL pattern name and this object's primary key.
        """
        return reverse('show_profile', kwargs={'pk': self.pk})

    
class StatusMessage(models.Model):
    """Model representing a status message posted by a user.
    
    Each status message is associated with a Profile through a foreign key
    relationship and includes a timestamp and message content.
    """
    
    # foreign key relationship to the Profile model
    # CASCADE delete means if profile is deleted, all associated status messages are deleted
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    # timestamp automatically set when status message is created/updated
    timestamp = models.DateTimeField(auto_now=True)
    
    # the actual status message content - required field
    message = models.TextField(blank=False)
    
    def __str__(self):
        """Return a string representation of this StatusMessage object."""
        return f'{self.message}'