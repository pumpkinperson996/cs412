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

from django.shortcuts import render

# import the Profile model to work with profile data
from .models import Profile
# import Django's generic class-based views for common operations
from django.views.generic import ListView, DetailView, CreateView
# import our custom forms for profile and status message creation
from .forms import CreateProfileForm, CreateStatusMessageForm
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
        """Handle the form submission and save the new object to the database.
        
        This method is called when the form data is valid. We need to
        add the foreign key (profile) to the StatusMessage object
        before saving it to the database.
        """
        
        # retrieve the profile primary key from the URL pattern
        pk = self.kwargs['pk']
        # get the Profile object that this status message belongs to
        profile = Profile.objects.get(pk=pk)
        # attach this profile to the status message before saving
        form.instance.profile = profile

        # delegate the actual saving work to the superclass method
        return super().form_valid(form)