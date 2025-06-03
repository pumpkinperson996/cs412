# File: urls.py
# Author: Shuwei Zhu (david996@bu.edu), 6/3/2025
# Description: URL Configuration for Mini Facebook Application.
# This module defines the URL patterns for the mini_fb application.
# It maps URL paths to their corresponding view classes.

"""
URL Patterns:
1. '' (empty string) - Root URL that displays all profiles
   - View: ShowAllProfilesView
   - Name: 'show_all_profiles'
   - Template: show_all_profiles.html
   
2. 'profile/<int:pk>' - Individual profile detail page
   - View: ShowProfilePageView
   - Name: 'show_profile'
   - Template: show_profile.html
   - Parameters: pk (primary key of the profile)

3. 'profile/create' - Page for creating a new profile
   - View: CreateProfileView
   - Name: 'create_profile'
   - Template: create_profile_form.html

4. 'profile/<int:pk>/create_status' - Page for creating a status message
   - View: CreateStatusMessageView
   - Name: 'create_status'
   - Template: create_status_form.html
   - Parameters: pk (primary key of the profile posting the status)
"""

from django.urls import path
# import all view classes from the views module
from .views import *

# list of URL patterns that map URLs to view classes
urlpatterns = [
    # map the root URL (empty string) to the view that shows all profiles
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    
    # map profile detail URLs with primary key parameter to profile detail view
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
    
    # map profile creation URL to the create profile view
    path('profile/create', CreateProfileView.as_view(), name='create_profile'),
    
    # map status message creation URL with profile primary key to create status view
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), 
         name='create_status'),
]