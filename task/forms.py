from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ShippingAddress
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateAddressForm(forms.Form):
    name = forms.CharField(required=False)
    surname = forms.CharField(required=False)
    mobile_phone = forms.CharField(required=False)
    country = shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    region = forms.CharField(required=False)
    postcode = forms.CharField(required=False)
