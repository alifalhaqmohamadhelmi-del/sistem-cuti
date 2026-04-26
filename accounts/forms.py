from django import forms
from .models import EmployeeProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['phone_number', 'address', 'department', 'position']
        # Tambah styling Bootstrap pada form
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }