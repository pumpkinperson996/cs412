# File: urls.py
# Author: Shuwei Zhu (david996@bu.edu), 6/25/2025
# Description: URL Configuration for Toilet App.
# This module defines the URL patterns for the toilet app.
# It maps URL paths to their corresponding view classes.

"""
URL Patterns:
1. '' (empty string) - Root URL that displays all restrooms with search
   - View: ShowAllRestroomsView
   - Name: 'show_all_restrooms'
   - Template: show_all_restrooms.html
   
2. 'restroom/<int:pk>' - Individual restroom detail page
   - View: ShowRestroomDetailView
   - Name: 'show_restroom'
   - Template: show_restroom_detail.html
   - Parameters: pk (primary key of the restroom)

3. 'restroom/create' - Page for creating a new restroom
   - View: CreateRestroomView
   - Name: 'create_restroom'
   - Template: create_restroom_form.html

4. 'restroom/<int:pk>/review' - Page for creating a review
   - View: CreateReviewView
   - Name: 'create_review'
   - Template: create_review_form.html
   - Parameters: pk (primary key of the restroom being reviewed)

5. 'stall/<int:pk>/update' - Update stall occupancy status
   - View: UpdateStallStatusView
   - Name: 'update_stall'
   - Template: update_stall_form.html
   - Parameters: pk (primary key of the stall)

6. 'restroom/<int:pk>/order' - Create supply order for restroom
   - View: CreateOrderView
   - Name: 'create_order'
   - Template: create_order_form.html
   - Parameters: pk (primary key of the restroom)

7. 'my-orders' - View user's order history
   - View: MyOrdersView
   - Name: 'my_orders'
   - Template: my_orders.html

8. 'restroom/<int:pk>/update' - Update restroom information
   - View: UpdateRestroomView
   - Name: 'update_restroom'
   - Template: update_restroom_form.html
   - Parameters: pk (primary key of the restroom)

9. 'review/<int:pk>/delete' - Delete a review
   - View: DeleteReviewView
   - Name: 'delete_review'
   - Template: delete_review_confirm.html
   - Parameters: pk (primary key of the review)
"""

from django.urls import path
from django.contrib.auth import views as auth_views

# import all view classes from the views module
from .views import (
    ShowAllRestroomsView,
    ShowRestroomDetailView,
    CreateRestroomView,
    CreateReviewView,
    UpdateStallStatusView,
    CreateOrderView,
    MyOrdersView,
    UpdateRestroomView,
    DeleteReviewView,
    RegisterView,
    CancelOrderView


)

# define app name for namespacing
app_name = 'toiletapp'

# list of URL patterns that map URLs to view classes
urlpatterns = [
    # map the root URL (empty string) to the view that shows all restrooms
    path('', ShowAllRestroomsView.as_view(), name='show_all_restrooms'),
    
    # map restroom detail URLs with primary key parameter to restroom detail view
    path('restroom/<int:pk>/', ShowRestroomDetailView.as_view(), name='show_restroom'),
    
    # map restroom creation URL to the create restroom view
    path('restroom/create/', CreateRestroomView.as_view(), name='create_restroom'),
    
    # map review creation URL with restroom primary key to create review view
    path('restroom/<int:pk>/review/', CreateReviewView.as_view(), name='create_review'),
    
    # map stall update URL with stall primary key to update stall view
    path('stall/<int:pk>/update/', UpdateStallStatusView.as_view(), name='update_stall'),
    
    # map order creation URL with restroom primary key to create order view
    path('restroom/<int:pk>/order/', CreateOrderView.as_view(), name='create_order'),
    
    # map user's orders URL to my orders view
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),
    
    # map restroom update URL with primary key to update restroom view
    path('restroom/<int:pk>/update/', UpdateRestroomView.as_view(), name='update_restroom'),
    
    # map review deletion URL with primary key to delete review view
    path('review/<int:pk>/delete/', DeleteReviewView.as_view(), name='delete_review'),
    
    # authentication URLs (these would typically be in the main project urls.py)
    # included here for completeness
    path('login/', auth_views.LoginView.as_view(template_name='toiletapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='toiletapp:show_all_restrooms'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('order/<int:pk>/cancel/', CancelOrderView.as_view(), name='cancel_order'),
]