# project/api_urls.py

from django.urls import path
from . import api_views

urlpatterns = [
    # Authentication related
    path('register/', api_views.register_user, name='api_register'),
    path('login/', api_views.login_user, name='api_login'),
    path('logout/', api_views.logout_user, name='api_logout'),
    
    # User related
    path('profile/', api_views.user_profile, name='api_profile'),
    path('profile/update/', api_views.update_profile, name='api_update_profile'),
    
    # Restroom related
    path('restrooms/', api_views.restroom_list, name='api_restroom_list'),
    path('restrooms/<int:restroom_id>/', api_views.restroom_detail, name='api_restroom_detail'),
    
    # Stall related
    path('stalls/<int:stall_id>/status/', api_views.update_stall_status, name='api_update_stall_status'),
    
    # Review related
    path('reviews/', api_views.reviews, name='api_reviews'),
    
    # Product related
    path('products/', api_views.product_list, name='api_product_list'),
    
    # Order related
    path('orders/', api_views.submit_order, name='api_submit_order'),
    path('orders/my/', api_views.user_orders, name='api_user_orders'),
]