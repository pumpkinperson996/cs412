from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [ 
    path(r'', views.main, name="mainpage"),
    path(r'order', views.show_form, name="orderpage"),
    path(r'submit', views.submit, name="submit"), 

]