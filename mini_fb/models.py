from django.db import models
from django.urls import reverse


class Profile(models.Model):

    # data attributes of a Article:
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email_address = models.TextField(blank=False)
    image_url = models.URLField(blank=True)
    
    def __str__(self):
        '''Return a string representation of this Article object.'''
        return f'{self.first_name}  {self.last_name}'
    
    def get_all_StatusMessage(self):
        '''Return all of the StatusMessage about this profile.'''

        AllStatusMessage = StatusMessage.objects.filter(profile=self)
        return AllStatusMessage
    
    def get_absolute_url(self):
        '''Return the URL to display one instance of this model.'''
        return reverse('show_profile', kwargs={'pk':self.pk})

    
class StatusMessage(models.Model):
    
    profile = models.ForeignKey(Profile, on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=False)
    
    def __str__(self):
        return f'{self.message}'