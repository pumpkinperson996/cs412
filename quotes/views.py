from django.shortcuts import render

# Create your views here.
from django.http import HttpRequest, HttpResponse
import random


# Create your views here.

quotelist = ["A rose by any other name would smell as sweet.", "All that glitters is not gold.", "All the world’s a stage, and all the men and women merely players."]

picturelist = ["https://d2cvjmix0699s1.cloudfront.net/resources/elephango/resourceFull/will-shakespeare-13330.jpg", 
               
               "https://cdn-test.poetryfoundation.org/cdn-cgi/image/w=2292,h=1528,q=80/content/images/653f5eeafab7a9895af1eca68e97459c831812c6.jpeg",
               
               "https://images2.minutemediacdn.com/image/upload/c_crop,x_0,y_0,w_3838,h_2158/c_fill,w_720,ar_16:9,f_auto,q_auto,g_auto/images/voltaxMediaLibrary/mmsport/mentalfloss/01hvvqn9pbe0z45dtkef.jpg"
               
]

def mainpage(request):
    template_name = "quotes/mainpage.html"

    context = {
        'quote': random.choice(quotelist),
        'picture': random.choice(picturelist)
    }
    
    return render(request, template_name, context)

def quote(request):
    template_name = "quotes/quote.html"

    context = {
        'quote': random.choice(quotelist),
        'picture': random.choice(picturelist)
    }
    
    return render(request, template_name, context)

def about(request):
    template_name = "quotes/about.html"


    
    return render(request, template_name)

def showall(request):
    template_name = "quotes/showall.html"

    context = {
        'quote': quotelist,
        'picture': picturelist,
    }
    
    return render(request, template_name, context)