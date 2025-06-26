# File: views.py
# Author: Shuwei Zhu (david996@bu.edu), 6/25/2025
# Description: View Classes for Toilet App.
# This module contains the view classes that handle HTTP requests and responses
# for the toilet app. It uses Django's generic class-based views for
# common patterns like listing, displaying details, and creating objects.

"""
Views:
1. ShowAllRestroomsView - Displays all restrooms with search/filter
2. ShowRestroomDetailView - Displays a single restroom's details, reviews, and stalls
3. CreateRestroomView - Handles creating new restrooms
4. CreateReviewView - Handles creating new reviews for a restroom
5. UpdateStallStatusView - Updates stall occupancy status
6. CreateOrderView - Handles supply ordering
7. MyOrdersView - Shows user's order history
8. UpdateRestroomView - Updates restroom information
9. DeleteReviewView - Deletes a review
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from decimal import Decimal
from .forms import RegisterForm


import json

# import models
from .models import Restroom, Review, Stall, Product, Order, User

# import forms
from .forms import (
    CreateRestroomForm, CreateReviewForm, UpdateStallStatusForm, 
    CreateOrderForm, SearchRestroomForm
)


class ShowAllRestroomsView(ListView):
    """Create a subclass of ListView to display all Restroom objects.
    
    This view retrieves all Restroom objects from the database with
    search and filter functionality.
    """

    # specify which model to retrieve objects from
    model = Restroom
    # specify which template to use for rendering the view
    template_name = 'toiletapp/show_all_restrooms.html'
    # specify the context variable name to access the data in the template
    context_object_name = 'restrooms'
    # enable pagination
    paginate_by = 12
    
    def get_queryset(self):
        """Override to add search and filter functionality."""
        queryset = super().get_queryset()
        
        # get search parameters from GET request
        search_query = self.request.GET.get('search_query', '')
        min_rating = self.request.GET.get('min_rating', '')
        has_available = self.request.GET.get('has_available_stalls', '')
        
        # apply search filter if query provided
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(address__icontains=search_query)
            )
        
        # apply rating filter if specified
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=int(min_rating))
        
        # apply availability filter if checked
        if has_available:
            # get restrooms with at least one unoccupied stall
            available_restrooms = []
            for restroom in queryset:
                if restroom.stalls.filter(is_occupied=False).exists():
                    available_restrooms.append(restroom.pk)
            queryset = queryset.filter(pk__in=available_restrooms)
        
        # order by average rating (highest first)
        return queryset.order_by('-avg_rating', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchRestroomForm(self.request.GET)
        restroom_stats = []
        for restroom in context['restrooms']:
            total = restroom.stalls.count()
            occupied = restroom.stalls.filter(is_occupied=True).count()
            available = total - occupied
            restroom_stats.append({
                'restroom': restroom,
                'occupied': occupied,
                'available': available,
                'total': total,
            })
        context['restroom_stats'] = restroom_stats
        return context


class ShowRestroomDetailView(DetailView):
    """Show the details for one Restroom object.
    
    This view displays detailed information about a single restroom,
    including reviews, stall status, and order options.
    """
    
    # specify which model this detail view is for
    model = Restroom
    # specify which template to use for rendering the restroom details
    template_name = 'toiletapp/show_restroom_detail.html'
    # specify the context variable name to access the restroom data in template
    context_object_name = 'restroom'
    
    def get_context_data(self, **kwargs):
        """Add additional context for reviews and stalls."""
        context = super().get_context_data(**kwargs)
        
        # get all reviews for this restroom, ordered by most recent
        context['reviews'] = Review.objects.filter(
            restroom=self.object
        ).order_by('-created_at')
        
        # get all stalls for this restroom
        context['stalls'] = Stall.objects.filter(
            restroom=self.object
        ).order_by('stall_no')
        
        # calculate occupancy statistics
        total_stalls = context['stalls'].count()
        occupied_stalls = context['stalls'].filter(is_occupied=True).count()
        context['available_stalls'] = total_stalls - occupied_stalls
        context['occupancy_percentage'] = (
            (occupied_stalls / total_stalls * 100) if total_stalls > 0 else 0
        )
        context['availability_percentage'] = (
            ((total_stalls - occupied_stalls) / total_stalls * 100) if total_stalls > 0 else 100
        )
        
        return context


class CreateRestroomView(LoginRequiredMixin, CreateView):
    """Handle creation of new Restroom objects.
    
    This view displays a form for creating new restrooms and processes
    the form submission to save new Restroom objects to the database.
    """
    
    # specify which form class to use for restroom creation
    form_class = CreateRestroomForm
    # specify which template to use for the restroom creation form
    template_name = "toiletapp/create_restroom_form.html"
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login') 
    
    def form_valid(self, form):
        """Process valid form submission."""
        # attach the current user as the creator
        form.instance.created_by = self.request.user
        
        # get number of stalls from form
        num_stalls = form.cleaned_data.get('num_stalls', 3)
        
        # save the restroom first
        restroom = form.save()
        
        # create the specified number of stalls
        for i in range(1, num_stalls + 1):
            Stall.objects.create(
                restroom=restroom,
                stall_no=i,
                is_occupied=False
            )
        
        # add success message
        messages.success(
            self.request, 
            f'Restroom "{restroom.name}" created successfully with {num_stalls} stalls!'
        )
        
        # redirect to the new restroom's detail page
        return redirect('toiletapp:show_restroom', pk=restroom.pk)


class CreateReviewView(LoginRequiredMixin, CreateView):
    """Handle creation of new Review objects.
    
    This view displays a form for creating reviews and processes
    the form submission. It automatically associates the review
    with the correct restroom based on the URL parameter.
    """
    
    # specify which form class to use for review creation
    form_class = CreateReviewForm
    # specify which template to use for the review creation form
    template_name = "toiletapp/create_review_form.html"
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login')
    
    def get_context_data(self, **kwargs):
        """Add the restroom to the context for the template."""
        context = super().get_context_data(**kwargs)
        # get restroom from URL parameter
        restroom_pk = self.kwargs.get('pk')
        context['restroom'] = get_object_or_404(Restroom, pk=restroom_pk)
        return context
    
    def form_valid(self, form):
        # Get the current restroom primary key
        restroom_pk = self.kwargs.get('pk')
        restroom = get_object_or_404(Restroom, pk=restroom_pk)
        # Check if the user has already submitted a review for this restroom
        if Review.objects.filter(restroom=restroom, author=self.request.user).exists():
            messages.error(self.request, "You have already reviewed this restroom!")
            return redirect('toiletapp:show_restroom', pk=restroom.pk)
        # Attach restroom and author to the review
        form.instance.restroom = restroom
        form.instance.author = self.request.user

        # Save the review
        review = form.save()

        # Handle photo uploads if any
        form.instance.author = self.request.user
        form.instance.restroom = get_object_or_404(Restroom, pk=self.kwargs.get('pk'))


        # Update restroom's average rating
        self.update_restroom_rating(restroom)

        # Show success message
        messages.success(self.request, 'Your review has been posted!')

        # Redirect to restroom detail page
        return redirect('toiletapp:show_restroom', pk=restroom.pk)

    
    def update_restroom_rating(self, restroom):
        """Recalculate and update restroom's average rating."""
        avg = Review.objects.filter(restroom=restroom).aggregate(
            Avg('rating')
        )['rating__avg']
        
        restroom.avg_rating = avg if avg else 0
        restroom.save()


class UpdateStallStatusView(LoginRequiredMixin, UpdateView):
    """Handle updating stall occupancy status.
    
    Allows users to mark stalls as occupied or available.
    """
    
    model = Stall
    form_class = UpdateStallStatusForm
    template_name = "toiletapp/update_stall_form.html"
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login')
    
    def get_success_url(self):
        """Redirect back to the restroom detail page after update."""
        return reverse('toiletapp:show_restroom', kwargs={'pk': self.object.restroom.pk})
    
    def form_valid(self, form):
        """Add success message on valid form submission."""
        response = super().form_valid(form)
        
        status = "occupied" if form.instance.is_occupied else "available"
        messages.success(
            self.request, 
            f'Stall {form.instance.stall_no} marked as {status}.'
        )
        
        return response


class CreateOrderView(LoginRequiredMixin, TemplateView):
    """Handle supply ordering for a restroom.
    
    Custom view for processing product orders with dynamic form.
    """
    
    template_name = "toiletapp/create_order_form.html"
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login')
    
    def get_context_data(self, **kwargs):
        """Add products and restroom to context."""
        context = super().get_context_data(**kwargs)
        
        # get restroom from URL
        restroom_pk = self.kwargs.get('pk')
        context['restroom'] = get_object_or_404(Restroom, pk=restroom_pk)
        
        # get all available products
        context['products'] = Product.objects.filter(stock_qty__gt=0)
        
        # create order form
        context['form'] = CreateOrderForm(self.request.POST or None)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Process order submission."""
        form = CreateOrderForm(request.POST)
        
        if form.is_valid():
            # get restroom
            restroom_pk = self.kwargs.get('pk')
            restroom = get_object_or_404(Restroom, pk=restroom_pk)
            
            # prepare order items and calculate total
            items = {}
            total_amount = Decimal('0.00')
            
            for field_name, quantity in form.cleaned_data.items():
                if field_name.startswith('product_') and quantity and quantity > 0:
                    product_id = int(field_name.replace('product_', ''))
                    product = Product.objects.get(pk=product_id)
                    
                    # add to items dict
                    items[str(product_id)] = quantity
                    
                    # calculate cost
                    total_amount += product.unit_price * quantity
                    
                    # update stock
                    product.stock_qty -= quantity
                    product.save()
            
            # create order
            order = Order.objects.create(
                buyer=request.user,
                restroom=restroom,
                items=items,
                total_amount=total_amount,
                status='pending'
            )
            
            messages.success(
                request, 
                f'Order #{order.id} placed successfully! Total: ${total_amount}'
            )
            
            return redirect('toiletapp:my_orders')
        
        # if form invalid, redisplay with errors
        return self.get(request, *args, **kwargs)


class MyOrdersView(LoginRequiredMixin, ListView):
    """Display user's order history."""
    
    model = Order
    template_name = 'toiletapp/my_orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login')
    
    def get_queryset(self):
        """Filter orders to show only current user's orders."""
        return Order.objects.filter(
            buyer=self.request.user
        ).order_by('-created_at')


class UpdateRestroomView(LoginRequiredMixin, UpdateView):
    """Handle updating restroom information.
    
    Only allows the creator to update their restroom.
    """
    
    model = Restroom
    fields = ['name', 'address']
    template_name = "toiletapp/update_restroom_form.html"
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login')
    
    def get_queryset(self):
        """Limit to restrooms created by current user."""
        return Restroom.objects.filter(created_by=self.request.user)
    
    def get_success_url(self):
        """Redirect to restroom detail page after update."""
        return reverse('toiletapp:show_restroom', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Add success message."""
        response = super().form_valid(form)
        messages.success(self.request, 'Restroom updated successfully!')
        return response


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    """Handle deleting reviews.
    
    Only allows authors to delete their own reviews.
    """
    
    model = Review
    template_name = "toiletapp/delete_review_confirm.html"
    
    def get_login_url(self):
        """Return the URL required for login."""
        return reverse('login')
    
    def get_queryset(self):
        """Limit to reviews by current user."""
        return Review.objects.filter(author=self.request.user)
    
    def get_success_url(self):
        """Redirect to restroom page after deletion."""
        return reverse('toiletapp:show_restroom', kwargs={'pk': self.object.restroom.pk})
    
    def delete(self, request, *args, **kwargs):
        """Update restroom rating after deleting review."""
        review = self.get_object()
        restroom = review.restroom
        
        # delete the review
        response = super().delete(request, *args, **kwargs)
        
        # update restroom average rating
        avg = Review.objects.filter(restroom=restroom).aggregate(
            Avg('rating')
        )['rating__avg']
        restroom.avg_rating = avg if avg else 0
        restroom.save()
        
        messages.success(request, 'Review deleted successfully.')
        
        return response
    
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'toiletapp/register.html'
    success_url = reverse_lazy('toiletapp:login')
    
class CancelOrderView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, buyer=request.user)
        order.status = 'cancelled'  
        order.save()
        return redirect('toiletapp:my_orders')