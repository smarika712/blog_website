from django import forms
from django.core.exceptions import ValidationError
from .models import Blog

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'author','image' ,'content']


def validate_upload(file):
    max_size = 5 * 1024 * 1024 

    if file.size > max_size:
        raise ValidationError("File size should not exceed 5 MB.")

    allowed_types = [
        'image/jpeg',
        'image/png',
        'application/pdf'
    ]

    if file.content_type not in allowed_types:
        raise ValidationError("Only JPG, PNG, and PDF files are allowed.")
    
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))