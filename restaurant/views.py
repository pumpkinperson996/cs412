from django.shortcuts import render
import random

from datetime import datetime, timedelta

# Create your views here.

dailyspecial = ["bibimap:14.99", "ice tea:3", "sweet potato fires:5"]
global_random_dailyspecial = []


def main(request):
    template_name = "restaurant/main.html"

    
    return render(request, template_name)

def show_form(request):
    '''Show the web page with the form.'''

    template_name = "restaurant/order.html"
    
    
    random_dailyspecial = random.choice(dailyspecial)
    
    # Split to get name and price separately for display
    special_name, special_price = random_dailyspecial.split(":")
    
    
    context = {
        'dailyspecial': random_dailyspecial,  # Full string for form value
        'special_name': special_name,         # Just the name for display
        'special_price': special_price,       # Just the price for display
    }
    return render(request, template_name, context)

def submit(request):
    '''Process the form submission, and generate a result.'''
    

    template_name = "restaurant/confirmation.html"
    
    context = {}


    # read the form data into python variables:
    if request.POST:

        Name = request.POST['Name']
        Email = request.POST['Email']
        Phone = request.POST['Phone']
        Instructions = request.POST['Instructions']
        
        selected_raw = request.POST.getlist('dishes')
        
        # Get daily special if selected
        daily_special_selected = request.POST.get('Specialbox')
        selected_dishes = []
        total_price = 0.0

        

        for item in selected_raw:
            dish_name, price_str = item.split(":")
            price = float(price_str)
            selected_dishes.append({'name': dish_name, 'price': price})
            total_price += price
            
        if daily_special_selected:
            dish_name, price_str = daily_special_selected.split(":")
            price = float(price_str)
            selected_dishes.append({'name': dish_name, 'price': price})
            total_price += price
            
        current_time = datetime.now()
        # Random number of minutes between 30 and 60
        minutes_to_add = random.randint(30, 60)
        ready_time = current_time + timedelta(minutes=minutes_to_add)
        
        
        

        context = {
            'name': Name,
            'email': Email,
            'phone':Phone,
            'instructions': Instructions,
            
            
            'selected_dishes': selected_dishes,
            'total_price': round(total_price, 2),
            'ready_time': ready_time,
            
        }

    return render(request, template_name, context=context)