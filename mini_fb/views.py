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

from django.contrib.auth.mixins import LoginRequiredMixin ## NEW
from django.contrib.auth.forms import UserCreationForm ## NEW
from django.contrib.auth.models import User ## NEW
from django.contrib.auth import login # NEW



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
    
    def dispatch(self, request, *args, **kwargs):
        '''Override the dispatch method to add debugging information.'''

        if request.user.is_authenticated:
            print(f'ShowAllProfilesView.dispatch(): request.user={request.user}')
        else:
            print(f'ShowAllProfilesView.dispatch(): not logged in.')

        return super().dispatch(request, *args, **kwargs)
    

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


class CreateProfileView(LoginRequiredMixin, CreateView):
    """Handle creation of new Profile objects.
    
    This view displays a form for creating new profiles and processes
    the form submission to save new Profile objects to the database.
    """
    
    # specify which form class to use for profile creation
    form_class = CreateProfileForm
    # specify which template to use for the profile creation form
    template_name = "mini_fb/create_profile_form.html"
    
    def get_login_url(self):
        '''return the URL required for login'''
        return reverse('login') 
    
    def form_valid(self, form):
        
        print(f'CreateProfileView: form.cleaned_data={form.cleaned_data}')
        
        # find the logged in user
        user = self.request.user
        print(f"CreateProfileView user={user} profile.user={user}")

        # attach user to form instance (Article object):
        form.instance.user = user

        return super().form_valid(form)
    
    

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    """Handle creation of new StatusMessage objects.
    
    This view displays a form for creating status messages and processes
    the form submission. It automatically associates the status message
    with the correct profile based on the URL parameter.
    """
    
    # specify which form class to use for status message creation
    form_class = CreateStatusMessageForm
    # specify which template to use for the status message creation form
    template_name = "mini_fb/create_status_form.html"
    
    def get_login_url(self):
        '''return the URL required for login'''
        return reverse('login') 
    
    def get_context_data(self, **kwargs):
        """Add the profile to the context for the template."""
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.filter(user=self.request.user).first()
        context['profile'] = profile
        return context
    
    def get_success_url(self):
        """Return the URL to redirect to after successfully submitting form.
        
        After creating a status message, redirect back to the profile page
        that the message was posted to.
        """
        profile = Profile.objects.filter(user=self.request.user).first()
        # generate and return the URL for the profile detail page
        return reverse('show_profile', kwargs={'pk': profile.pk})

    def form_valid(self, form):
        # Get the profile
        profile = Profile.objects.filter(user=self.request.user).first()
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
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"
    
    def get_login_url(self):
        '''return the URL required for login'''
        return reverse('login') 
    def get_object(self):
        '''Return the Profile object for the logged-in user'''
        return Profile.objects.filter(user=self.request.user).first()
        
    
class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = 'status_message'
    
    def get_login_url(self):
        '''return the URL required for login'''
        return reverse('login') 
    
    def get_success_url(self):
        '''Return a the URL to which we should be directed after the delete.'''
        
        # get the pk for this status message
        pk = self.kwargs.get('pk')
        status_message = StatusMessage.objects.get(pk=pk)
        
        # find the profile to which this StatusMessage is related by FK
        profile = status_message.profile
        
        # reverse to show the profile page
        return reverse('show_profile', kwargs={'pk': profile.pk})
    

class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    model = StatusMessage
    fields = ['message']  # Only allow updating the message text
    template_name = "mini_fb/update_status_form.html"
    
    def get_login_url(self):
        '''return the URL required for login'''
        return reverse('login') 
    
    def get_success_url(self):
        # After update, return to the profile page
        pk = self.kwargs.get('pk')
        status_message = StatusMessage.objects.get(pk=pk)
        profile = status_message.profile
        return reverse('show_profile', kwargs={'pk': profile.pk})
    
class AddFriendView(LoginRequiredMixin, View):
    """Handle adding a friend relationship between two profiles.
    
    This view processes the add friend action from URL parameters
    without requiring a form. It reads profile PKs from the URL,
    creates the friendship, and redirects back to the profile page.
    """
    
    def get_login_url(self):
        '''return the URL required for login'''
        return reverse('login') 
    
    def dispatch(self, request, *args, **kwargs):
        """Process the add friend request.
        
        Creates friend relationship between logged-in user's profile
        and the other profile specified in URL.
        """
        # Get the other profile PK from URL parameters
        other_pk = self.kwargs.get('other_pk')  # Profile to add as friend
        
        # Get profile for logged-in user
        profile = Profile.objects.filter(user=request.user).first()
        
        # Check if profile exists
        if not profile:
            # If no profile exists for this user, redirect to create profile
            return redirect('create_profile')
        
        try:
            # Get the other profile
            other_profile = Profile.objects.get(pk=other_pk)
            
            # Use the add_friend method to create the friendship
            profile.add_friend(other_profile)
            
        except Profile.DoesNotExist:
            # Handle case where the other profile doesn't exist
            # Still redirect to the user's profile
            pass
        
        # Always redirect back to the logged-in user's profile page
        return redirect('show_profile', pk=profile.pk)

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
    
    def get_object(self):
        '''Return the Profile object for the logged-in user'''
        return Profile.objects.filter(user=self.request.user).first()

        
    
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
    
    def get_object(self):
        '''Return the Profile object for the logged-in user'''
        return Profile.objects.filter(user=self.request.user).first()
        
    
    
class RegistrationView(CreateView):
    '''
    show/process form for account registration
    '''

    template_name = 'blog/register.html'
    form_class = UserCreationForm
    model = User
    
    def get_success_url(self):
        '''The URL to redirect to after creating a new User.'''
        return reverse('login')
