import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from catalog.models import User, Customer, Expedition, Trip


def name_validation(first_name, last_name):
    errors = {}
    if any(char.isdigit() for char in first_name):
        errors['first_name'] = _('First name cannot contain numbers.')
    if any(char.isdigit() for char in last_name):
        errors['last_name'] = _('Last name cannot contain numbers.')
    return errors


class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.RegexField(regex=r'^\+\d{8,15}', max_length=16, required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_number')

    def clean(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        errors = name_validation(first_name, last_name)
        if errors:
            raise ValidationError(errors)


class EditCustomerProfile(forms.ModelForm):
    # bud takto alebo cez clean_phone_number
    phone_number = forms.RegexField(regex=r'^\+\d{8,15}', max_length=16, required=False)

    class Meta:
        model = Customer
        fields = ['phone_number']

    # alebo takto no
    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data['phone_number']
    #     if not re.match(r'^\+\d{8,15}$', phone_number):
    #         raise ValidationError(_('Invalid phone number.'))
    #     return phone_number


class EditUserProfile(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def clean(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        errors = name_validation(first_name, last_name)
        if errors:
            raise ValidationError(errors)


class BaseTripFormSet(forms.BaseModelFormSet):
    # toto uz myslim nepotrebujem, lebo jednak extra=0 a druhak vo validation mam, ze vsetko vo forme je required
    # def __init__(self, *args, **kwargs):
    #     super(BaseTripFormSet, self).__init__(*args, **kwargs)
    #     for form in self.forms:
    #         form.empty_permitted = False

    def clean(self):
        """Check that no trips have the same park."""

        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        parks = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            park = form.cleaned_data['park']    # TODO check if park exists
            if park:
                if park in parks:
                    raise ValidationError(_('Trips can\'t have the same park.'))
                parks.append(park)


class ExpeditionForm(forms.ModelForm):
    class Meta:
        model = Expedition
        fields = ['number_of_people', 'message_for_us']

    def clean_number_of_people(self):
        number_of_people = self.cleaned_data['number_of_people']
        if not number_of_people:
            raise ValidationError(_('Enter number of people.'))
        return number_of_people


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['park', 'accommodation', 'days']

    # This is for recommended expeditions. We need to set it, otherwise it wouldn't save for a user
    # in case he wants the same trip (he didn't change anything, so save() would ignore this form without this override)
    def has_changed(self):
        return True

