from django import forms
from .models import Ticket, Comment, MyUser
from django.contrib.auth.forms import UserCreationForm


# Custom user creation form with role selection
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ("username", "email", "role")


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
