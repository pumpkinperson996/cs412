from django import forms
from .models import Profile, StatusMessage

class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email_address', 'image_url']
        
        
class CreateStatusMessageForm(forms.ModelForm):
    class Meta:
        '''associate this form with the Comment model; select fields.'''
        model = StatusMessage
        fields = ['message']  # which fields from model should we use

