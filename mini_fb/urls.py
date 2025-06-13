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

from django.contrib.auth import views as auth_views    ## NEW


# list of URL patterns that map URLs to view classes
urlpatterns = [
    # map the root URL (empty string) to the view that shows all profiles
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'),
    
    # map profile detail URLs with primary key parameter to profile detail view
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
    
    # map profile creation URL to the create profile view
    path('profile/create', CreateProfileView.as_view(), name='create_profile'),
    
    # map status message creation URL with profile primary key to create status view
    path('status/create_status', CreateStatusMessageView.as_view(), name='create_status'),

    
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),
    
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),
    
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),
    
    # map add friend URL with two profile PKs to the add friend view
    path('profile/add_friend/<int:other_pk>', AddFriendView.as_view(), name='add_friend'),
    
    # map friend suggestions URL to show friend suggestions view
    path('profile/friend_suggestions', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    
    # map news feed URL to show news feed view
    path('profile/news_feed', ShowNewsFeedView.as_view(), name='news_feed'),

    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'), ## NEW
    
	 path('logout/', auth_views.LogoutView.as_view(next_page='show_all_profiles'), name='logout'), ## NEW


    
   path('register/', RegistrationView.as_view(), name='register'),

    
    
]