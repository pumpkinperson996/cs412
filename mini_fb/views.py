"""
views.py - View Classes for Mini Facebook Application

This module contains the view classes that handle HTTP requests and responses
for the mini_fb application. It uses Django's generic class-based views for
common patterns like listing and displaying details.

Views:
1. ShowAllProfilesView - Displays all user profiles
2. ShowProfilePageView - Displays a single profile's details


Author: Shuwei Zhu
Date: 5/29/2025
"""

from django.shortcuts import render

# Create your views here.
from .models import Profile
from django.views.generic import ListView, DetailView, CreateView
from .forms import CreateProfileForm, CreateStatusMessageForm
from django.urls import reverse




class ShowAllProfilesView(ListView):
    '''Create a subclass of ListView to display all Profile.'''

    model = Profile # retrieve objects of type Profile from the database
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles' # how to find the data in the template file
    
class ShowProfilePageView(DetailView):
    '''Show the details for one Profile.'''
    model = Profile
    template_name = 'mini_fb/show_profile.html' 
    context_object_name = 'profiles'

class CreateProfileView(CreateView):
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"
    
class CreateStatusMessageView(CreateView):
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"
    
    def get_success_url(self):
        '''Return the URL to redirect to after successfully submitting form.'''
        pk = self.kwargs['pk']
        return reverse('show_profile', kwargs={'pk':pk})

    
    def form_valid(self, form):
        '''This method handles the form submission and saves the 
        new object to the Django database.
        We need to add the foreign key (of the Article) to the Comment
        object before saving it to the database.
        '''
        
		
        
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        # attach this article to the comment
        form.instance.article = profile # set the FK

        # delegate the work to the superclass method form_valid:
        return super().form_valid(form)

    