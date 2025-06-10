# File: views.py
# Author: Shuwei Zhu (david996@bu.edu), 6/3/2025
# Description: View Classes for Mini Facebook Application.
# This module contains the view classes that handle HTTP requests and responses
# for the mini_fb application. It uses Django's generic class-based views for
# common patterns like listing, displaying details, and creating objects.

"""
Views:
1. ShowAllProfilesView - Displays all user profiles in a list
2. ShowProfilePageView - Displays a single profile's details and status messages
3. CreateProfileView - Handles creating new user profiles
4. CreateStatusMessageView - Handles creating new status messages for a profile
"""

from django.shortcuts import render, redirect

# import the Profile model to work with profile data
from .models import Profile, StatusMessage
# import Django's generic class-based views for common operations
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
# import our custom forms for profile and status message creation
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
# import reverse function for URL generation
from django.urls import reverse


class ShowAllProfilesView(ListView):
    """Create a subclass of ListView to display all Profile objects.
    
    This view retrieves all Profile objects from the database and displays
    them in a list format using the specified template.
    """

    # specify which model to retrieve objects from
    model = Profile
    # specify which template to use for rendering the view
    template_name = 'mini_fb/show_all_profiles.html'
    # specify the context variable name to access the data in the template
    context_object_name = 'profiles'
    

class ShowProfilePageView(DetailView):
    """Show the details for one Profile object.
    
    This view displays detailed information about a single profile,
    including associated status messages.
    """
    
    # specify which model this detail view is for
    model = Profile
    # specify which template to use for rendering the profile details
    template_name = 'mini_fb/show_profile.html'
    # specify the context variable name to access the profile data in template
    context_object_name = 'profiles'


class CreateProfileView(CreateView):
    """Handle creation of new Profile objects.
    
    This view displays a form for creating new profiles and processes
    the form submission to save new Profile objects to the database.
    """
    
    # specify which form class to use for profile creation
    form_class = CreateProfileForm
    # specify which template to use for the profile creation form
    template_name = "mini_fb/create_profile_form.html"
    
    

class CreateStatusMessageView(CreateView):
    """Handle creation of new StatusMessage objects.
    
    This view displays a form for creating status messages and processes
    the form submission. It automatically associates the status message
    with the correct profile based on the URL parameter.
    """
    
    # specify which form class to use for status message creation
    form_class = CreateStatusMessageForm
    # specify which template to use for the status message creation form
    template_name = "mini_fb/create_status_form.html"
    
    def get_context_data(self, **kwargs):
        """Add the profile to the context for the template."""
        context = super().get_context_data(**kwargs)
        # Get the profile from the URL
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile
        return context
    
    def get_success_url(self):
        """Return the URL to redirect to after successfully submitting form.
        
        After creating a status message, redirect back to the profile page
        that the message was posted to.
        """
        # retrieve the profile primary key from the URL parameters
        pk = self.kwargs['pk']
        # generate and return the URL for the profile detail page
        return reverse('show_profile', kwargs={'pk': pk})

    def form_valid(self, form):
        # Get the profile
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        form.instance.profile = profile
        
        # Save the status message first
        sm = form.save()
        
        # Handle file uploads
        files = self.request.FILES.getlist('files')

        
        # Import the Image and StatusImage models
        from .models import Image, StatusImage
        
        # Process each uploaded file
        for file in files:
            # Create an Image object for each uploaded file
            image = Image.objects.create(
                profile=profile,
                image_file=file,
                caption=''  # You can add caption functionality later
            )

            
            # Create StatusImage to link the image with the status message
            StatusImage.objects.create(
                status_message=sm,
                image=image
            )
        
        # Return to the profile page

        return redirect(self.get_success_url())
    
class UpdateProfileView(UpdateView):
    
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"
    
    
class DeleteStatusMessageView(DeleteView):
    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = 'status_message'
    
    def get_success_url(self):
        '''Return a the URL to which we should be directed after the delete.'''
        
        # get the pk for this status message
        pk = self.kwargs.get('pk')
        status_message = StatusMessage.objects.get(pk=pk)
        
        # find the profile to which this StatusMessage is related by FK
        profile = status_message.profile
        
        # reverse to show the profile page
        return reverse('show_profile', kwargs={'pk': profile.pk})
    

class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    fields = ['message']  # Only allow updating the message text
    template_name = "mini_fb/update_status_form.html"
    
    def get_success_url(self):
        # After update, return to the profile page
        pk = self.kwargs.get('pk')
        status_message = StatusMessage.objects.get(pk=pk)
        profile = status_message.profile
        return reverse('show_profile', kwargs={'pk': profile.pk})
    
class AddFriendView(View):
    """Handle adding a friend relationship between two profiles.
    
    This view processes the add friend action from URL parameters
    without requiring a form. It reads profile PKs from the URL,
    creates the friendship, and redirects back to the profile page.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Process the add friend request.
        
        Reads profile PKs from URL parameters, validates them,
        and creates the friend relationship if valid.
        """
        # Get the profile PKs from URL parameters
        pk = self.kwargs.get('pk')  # Profile doing the adding
        other_pk = self.kwargs.get('other_pk')  # Profile to add as friend
        
        # Retrieve the Profile objects from the database
        try:
            profile = Profile.objects.get(pk=pk)
            other_profile = Profile.objects.get(pk=other_pk)
            
            # Use the add_friend method to create the friendship
            profile.add_friend(other_profile)
            
        except Profile.DoesNotExist:
            # Handle case where one of the profiles doesn't exist
            pass
        
        # Redirect back to the profile page
        return redirect('show_profile', pk=pk)


class ShowFriendSuggestionsView(DetailView):
    """Display friend suggestions for a specific profile.
    
    Shows a list of profiles that the user could add as friends,
    excluding existing friends and the profile itself.
    """
    
    # Specify the model to use
    model = Profile
    # Template for displaying friend suggestions
    template_name = 'mini_fb/friend_suggestions.html'
    # Context variable name for the profile
    context_object_name = 'profile'
    
    
class ShowNewsFeedView(DetailView):
    """Display the news feed for a specific profile.
    
    Shows status messages from the profile and all their friends,
    ordered by most recent first.
    """
    
    # Specify the model to use
    model = Profile
    # Template for displaying the news feed
    template_name = 'mini_fb/news_feed.html'
    # Context variable name for the profile
    context_object_name = 'profile'