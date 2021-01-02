from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from catalog.models import User


class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.RegexField(regex=r'^\+\d{8,15}', max_length=16)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name', 'last_name')
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
