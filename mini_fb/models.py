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
    # image_url = models.URLField(blank=True)
    image_file = models.ImageField(blank=True) # an actual image
    
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
    
    def get_friends(self):
        """Return a list of all Profile objects that are friends with this profile.
        
        Searches for Friend relationships where this profile is either
        profile1 or profile2, and returns the other profile in each relationship.
        """
        # Import Friend model here to avoid circular import
        # Get all Friend objects where this profile is profile1
        friends_as_profile1 = Friend.objects.filter(profile1=self)
        
        # Get all Friend objects where this profile is profile2  
        friends_as_profile2 = Friend.objects.filter(profile2=self)
        
        # Create list to store friend profiles
        friend_profiles = []
        
        # Add friends where this profile is profile1 (get profile2)
        for friendship in friends_as_profile1:
            friend_profiles.append(friendship.profile2)
            
        # Add friends where this profile is profile2 (get profile1)
        for friendship in friends_as_profile2:
            friend_profiles.append(friendship.profile1)
            
        # Return the list of friend Profile objects
        return friend_profiles

    def add_friend(self, other):
        """Add a friend relationship between this profile and another profile.
        
        Creates a Friend instance connecting self and other if:
        - No existing friendship exists between them
        - The profiles are not the same (no self-friending)
        
        Args:
            other: Another Profile instance to create friendship with
        """
        # Check if trying to friend themselves
        if self == other:
            # Don't allow self-friending
            return
            
        # Check if friendship already exists in either direction
        # Check if self is profile1 and other is profile2
        existing_friendship1 = Friend.objects.filter(
            profile1=self, 
            profile2=other
        ).exists()
        
        # Check if other is profile1 and self is profile2
        existing_friendship2 = Friend.objects.filter(
            profile1=other, 
            profile2=self
        ).exists()
        
        # If no existing friendship in either direction, create new Friend instance
        if not existing_friendship1 and not existing_friendship2:
            # Create and save new Friend relationship
            new_friendship = Friend(profile1=self, profile2=other)
            new_friendship.save()
    
    def get_friend_suggestions(self):
        """Return a list of Profiles that could be friend suggestions.
        
        Returns profiles that are:
        - Not already friends with this profile
        - Not this profile itself
        """
        # Get all profiles
        all_profiles = Profile.objects.all()
        
        # Get current friends
        current_friends = self.get_friends()
        
        # Create list for suggestions
        suggestions = []
        
        # Check each profile
        for profile in all_profiles:
            # Skip if it's the same profile
            if profile == self:
                continue
            # Skip if already friends
            if profile in current_friends:
                continue
            # Add to suggestions
            suggestions.append(profile)
            
        # Return the list of suggested profiles
        return suggestions
    
    
    def get_news_feed(self):
        """Return a QuerySet of StatusMessages for this profile's news feed.
        
        The news feed includes:
        - All status messages posted by this profile
        - All status messages posted by friends of this profile
        Ordered by most recent first.
        """
        # Import StatusMessage model here to avoid circular import at top of file
        from .models import StatusMessage
        
        # Get list of friends
        friends = self.get_friends()
        
        # Create list to hold all profiles whose statuses we want
        profiles_to_include = [self]  # Start with self
        
        # Add all friends to the list
        profiles_to_include.extend(friends)
        
        # Use Django ORM to filter StatusMessages
        # Get all status messages where profile is in our list
        news_feed = StatusMessage.objects.filter(
            profile__in=profiles_to_include
        ).order_by('-timestamp')  # Order by most recent first
        
        # Return the QuerySet of status messages
        return news_feed
    
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
    
    def get_images(self):
        """Return all Images associated with this StatusMessage."""
        # Get all StatusImage objects for this status message
        status_images = StatusImage.objects.filter(status_message=self)
        # Extract the Image objects
        images = [si.image for si in status_images]
        return images
    
class Image(models.Model):
    """Model representing an image uploaded by a user."""
    
    # Foreign key to the Profile who uploaded this image
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    
    # The actual image file
    image_file = models.ImageField(blank=False)
    
    # Timestamp when the image was uploaded
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional caption for the image
    caption = models.TextField(blank=True)
    
    def __str__(self):
        return f"Image uploaded by {self.profile} at {self.timestamp}"
    
    
    
class StatusImage(models.Model):
    """Model representing the relationship between StatusMessage and Image."""
    
    # Foreign key to the StatusMessage
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE)
    
    # Foreign key to the Image
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Image for status: {self.status_message}"
    

class Friend(models.Model):
    """Model representing a friendship relationship between two profiles.
    
    This model creates an edge in the social network graph connecting
    two Profile nodes as friends.
    """
    
    # First profile in the friendship relationship
    # related_name prevents reverse accessor conflicts
    profile1 = models.ForeignKey(Profile, 
                                on_delete=models.CASCADE, 
                                related_name="profile1")
    
    # Second profile in the friendship relationship
    profile2 = models.ForeignKey(Profile, 
                                on_delete=models.CASCADE, 
                                related_name="profile2")
    
    # Timestamp when the friendship was created
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """Return a string representation of this Friend relationship."""
        # Display both profiles' names in the friendship
        return f"{self.profile1.first_name} {self.profile1.last_name} & {self.profile2.first_name} {self.profile2.last_name}"