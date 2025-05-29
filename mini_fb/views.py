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
from django.views.generic import ListView, DetailView



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
