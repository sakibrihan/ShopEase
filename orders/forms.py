from django import forms


class ShippingForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'placeholder': 'Full Name',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email Address',
    }))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'placeholder': 'Phone Number',
    }))
    address = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Street Address',
        'rows': 3,
    }))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'City',
    }))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'State',
    }))
    postal_code = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'placeholder': 'PIN / Postal Code',
    }))
