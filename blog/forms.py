from django import forms
from .models import Article
from .models import Comment


class CreateArticleForm(forms.ModelForm):
    
    class Meta:
        '''associate this form with a model from our database.'''
        model = Article
        fields = ['author', 'title', 'text', 'image_file']
        
class CreateCommentForm(forms.ModelForm):
    '''A form to add a Comment to the database.'''

    class Meta:
        '''associate this form with the Comment model; select fields'''
        model = Comment
        fields = ['author', 'text', ]  # which fields from model should we use
        

class UpdateArticleForm(forms.ModelForm):
    '''A form to update a quote to the database.'''

    class Meta:
        '''associate this form with the Article model.'''
        model = Article
        fields = ['title', 'text', ]  # which fields from model should we use