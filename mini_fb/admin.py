# File: admin.py
# Author: Shuwei Zhu (david996@bu.edu), 6/3/2025
# Description: Django admin configuration for the mini_fb application.
# Registers models with the Django admin interface for easy management.

from django.contrib import admin

# import our custom models to register them with the admin interface
from .models import Profile, StatusMessage

# register the Profile model with Django admin
# this allows CRUD operations on Profile objects through the admin interface
admin.site.register(Profile)

# register the StatusMessage model with Django admin
# this allows CRUD operations on StatusMessage objects through the admin interface
admin.site.register(StatusMessage)