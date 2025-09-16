from django import forms
from .models import MyUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['username', 'gender', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
