# voter_analytics/urls.py
from django.urls import path
from . import views

app_name = 'voter_analytics'

urlpatterns = [
    path('', views.VoterListView.as_view(), name='voters'),
    path('voter/<int:pk>/', views.VoterDetailView.as_view(), name='voter'),
    path('graphs/', views.VoterGraphsView.as_view(), name='graphs'),
]