from .models import JobApplication
from django import forms
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['name', 'email', 'phone', 'resume', 'cover_letter']
        widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
                'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
                'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
                'resume': forms.FileInput(attrs={'class': 'form-control'}),
                'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Cover Letter', 'rows': 5}),
        }