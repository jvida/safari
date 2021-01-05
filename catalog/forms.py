import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from catalog.models import User
from catalog.models import Customer


class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.RegexField(regex=r'^\+\d{8,15}', max_length=16)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_number')
    #     # model = User
    #     fields

    # def clean_username(self):
    #     data = self.cleaned_data['username']
    #
    #     # Check if a nickname isn't in use already
    #     if User.objects.filter(username=data):
    #         raise ValidationError(_('Given username is already in use.'))
    #
    #     return data


class EditCustomerProfile(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['phone_number']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+\d{8,15}$', phone_number):
            raise ValidationError(_('Invalid phone number.'))
        return phone_number


class EditUserProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def clean(self):
        errors = {}
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        if any(char.isdigit() for char in first_name):
            errors['first_name'] = _('First name cannot contain numbers.')
            # raise ValidationError(_('First name cannot contain numbers.'))
        if any(char.isdigit() for char in last_name):
            errors['last_name'] = _('Last name cannot contain numbers.')
            # raise ValidationError(_('Last name cannot contain numbers.'))
        if errors:
            raise ValidationError(errors)
