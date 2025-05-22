from django.urls import path
from django.conf import settings
from django.conf.urls.static import static    ## add for static files

from . import views

urlpatterns = [ 
    path(r'', views.mainpage, name="mainpage"),
    path(r'quote', views.quote, name="quotepage"),
    path(r'about', views.about, name="aboutpage"),
    path(r'showall', views.showall, name="showallpage"),
    
    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
