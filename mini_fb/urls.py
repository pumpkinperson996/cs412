"""
urls.py - URL Configuration for Mini Facebook Application

This module defines the URL patterns for the mini_fb application.
It maps URL paths to their corresponding view classes.

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
"""
from django.urls import path
from .views import *
urlpatterns = [
    # map the URL (empty string) to the view
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'), # generic class-based view
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
    path('profile/create', CreateProfileView.as_view(), name='create_profile'),
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    
]