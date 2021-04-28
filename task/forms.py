from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ShippingAddress
from django import forms


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateAddressForm(forms.Form):
    name = forms.CharField(required=False)
    surname = forms.CharField(required=False)
    mobile_phone = forms.CharField(required=False)
    country = forms.CharField(required=False)
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    region = forms.CharField(required=False)
    postcode = forms.CharField(required=False)
