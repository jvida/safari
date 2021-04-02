import re
from datetime import date
from django import forms
from django.core.files import File

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from catalog.models import User, Customer, Expedition, Trip, Feedback


def name_validation(first_name, last_name):
    errors = {}
    if any(char.isdigit() for char in first_name):
        errors['first_name'] = _('First name cannot contain numbers.')
    if any(char.isdigit() for char in last_name):
        errors['last_name'] = _('Last name cannot contain numbers.')
    return errors


def img_validation(picture, mb_limit):
    errors = {}
    # if it's str, it's loaded frim DB => not updated picture => no need to check it
    if not isinstance(picture, str):
        if picture:
            if picture.size > mb_limit * 1024 * 1024:
                errors['picture'] = _(f'Image file too large ( > {mb_limit}mb )')
    return errors


def date_validation(date_of_trip, oldest_allowed, newest_allowed):
    errors = {}

    if date_of_trip < oldest_allowed:
        errors['date_of_trip'] = _('ERROR too old')
    elif date_of_trip > newest_allowed:
        errors['date_of_trip'] = _('ERROR too young')
    return errors


class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.RegexField(regex=r'^\+\d{8,15}', max_length=16, required=False, help_text='Enter your phone '
                                                                                                   'number in '
                                                                                                   'international '
                                                                                                   'format. (e.g. '
                                                                                                   '+421944123132)')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_number')

    def clean(self):
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']

        # validation of first and last name
        errors = name_validation(first_name, last_name)

        # validation of username - checking whether already exists in DB or nor
        if User.objects.filter(username=username).exists():
            errors['username'] = _('The username is already in use. Please use a different username.')
        if User.objects.filter(email=email).exists():
            errors['email'] = _('The email is already in use. Please use a different email.')
        if errors:
            raise ValidationError(errors)


class EditCustomerProfile(forms.ModelForm):
    # bud takto alebo cez clean_phone_number
    phone_number = forms.RegexField(regex=r'^\+\d{8,15}', max_length=16, required=False)

    class Meta:
        model = Customer
        fields = ['phone_number', 'picture']

    def clean(self):
        picture = self.cleaned_data["picture"]
        errors = img_validation(picture, mb_limit=1)

        if errors:
            raise ValidationError(errors)

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
        username = self.cleaned_data['username']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']

        errors = {}

        # validate only if name fields were modified
        if first_name != self.instance.first_name or last_name != self.instance.last_name:
            errors = name_validation(first_name, last_name)

        # validate only if username field was modified
        if username != self.instance.username:
            # validation of username - checking whether already exists in DB or nor
            if User.objects.filter(username=username).exists():
                errors['username'] = _('The username is already in use. Please use a different username.')

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

        # toto som pre teraz vynechal, nech to rovno ukaze aj error o rovnakych parkoch spolu s ostatnymi errormi
        # if any(self.errors):
        #     # Don't bother validating the formset unless each form is valid on its own
        #     return

        parks = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            park = form.cleaned_data['park']    # TODO check if park exists
            if park:
                if park in parks:
                    form.add_error('park', 'Trips can\'t have same parks.')
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

    # toto by som pouzil, aby form ukazal warning, ze field musi byt filled
    # ale bohuzial u tripformsetu je problem, ze modelfactory ten input html negeneruje s required
    # takze aby som to mal konzistentne, tak tu si budem riesit required sam svojim errorom
    # a preto nepouzijem toto, ale az to nad tymto, aj ked to bude inak ako u register formularu
    # def __init__(self, *args, **kwargs):
    #     super(ExpeditionForm, self).__init__(*args, **kwargs)
    #     self.fields['number_of_people'].required = True


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['park', 'accommodation', 'days']

    # This is for recommended expeditions. We need to set it, otherwise it wouldn't save for a user
    # in case he wants the same trip (he didn't change anything, so save() would ignore this form without this override)
    def has_changed(self):
        return True


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["content", "date_of_trip"]
        widgets = {
            'date_of_trip': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        date_of_trip = self.cleaned_data['date_of_trip']
        oldest_allowed = date(year=2017, month=1, day=1)
        newest_allowed = date.today()

        errors = date_validation(date_of_trip, oldest_allowed=oldest_allowed, newest_allowed=newest_allowed)

        if errors:
            raise ValidationError(errors)
