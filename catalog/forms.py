import re
from datetime import date, timedelta
from django import forms
from django.core.files import File

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from catalog.models import User, Customer, Expedition, Trip, Feedback, Park


def name_validation(first_name, last_name):
    errors = {}
    if any(char.isdigit() for char in first_name):
        errors['first_name'] = _('First name cannot contain numbers.')
    if any(char.isdigit() for char in last_name):
        errors['last_name'] = _('Last name cannot contain numbers.')
    return errors


def img_validation(picture, mb_limit):
    errors = {}
    # if it's str, it's loaded from DB => not updated picture => no need to check it
    if not isinstance(picture, str):
        if picture:
            if picture.size > mb_limit * 1024 * 1024:
                errors['picture'] = _(f'Image file too large ( > {mb_limit}mb )')
    return errors


def date_validation(errors, given_date, newest_allowed, oldest_allowed, error_field, error_msg):
    if given_date < newest_allowed or given_date > oldest_allowed:
        errors[error_field] = _(error_msg)
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
            park = form.cleaned_data.get('park')    # get method returns None if it doesnt exist
            if park:
                if park in parks:
                    form.add_error('park', 'Trips can\'t have same parks.')
                parks.append(park)


class ExpeditionForm(forms.ModelForm):
    # date_from = forms.DateField(required=True)
    # date_to = forms.DateField(required=True)

    class Meta:
        model = Expedition
        fields = ['date_from', 'date_to', 'number_of_people', 'message_for_us']
        widgets = {
            'date_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        date_from = self.cleaned_data['date_from']
        date_to = self.cleaned_data['date_to']
        number_of_people = self.cleaned_data['number_of_people']

        errors = {}

        if not date_from:
            errors['date_from'] = _('Enter date.')
        else:
            newest_allowed = date.today() + timedelta(days=1)
            oldest_allowed = date.today() + timedelta(days=730)
            error_msg = 'Invalid date. Soonest allowed is tomorrow, latest allowed is today in 2 years.'
            errors = date_validation(errors, date_from, newest_allowed=newest_allowed, oldest_allowed=oldest_allowed,
                                     error_field='date_from', error_msg=error_msg)

        if not date_to:
            errors['date_to'] = _('Enter date.')
        else:
            newest_allowed = date.today() + timedelta(days=1+3)
            oldest_allowed = date.today() + timedelta(days=730)
            error_msg = 'Invalid date. Soonest allowed is tomorrow+3days (in case of a 2-day safari),' \
                        ' latest allowed is today in 2 years.'
            errors = date_validation(errors, date_to, newest_allowed=newest_allowed, oldest_allowed=oldest_allowed,
                                     error_field='date_to', error_msg=error_msg)

        if not ('date_from' in errors) and not ('date_to' in errors):
            if date_from > date_to:
                errors['date_from'] = _('Invalid date. "Date from" can\'t be later than "Date to"')
            elif (date_to - date_from).days < 3:
                errors['date_to'] = _('Invalid date. Minimum 3 days (in case of a 2-day safari)')

        if not number_of_people:
            errors['number_of_people'] = _('Enter number of people.')

        if errors:
            raise ValidationError(errors)

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
        newest_allowed = date.today() - timedelta(days=365*3)
        oldest_allowed = date.today()

        errors = {}
        error_msg = 'Invalid date. Latest allowed is today, soonest allowed is 3 years ago.'
        errors = date_validation(errors=errors, given_date=date_of_trip, newest_allowed=newest_allowed,
                                 oldest_allowed=oldest_allowed, error_field='date_of_trip', error_msg=error_msg)

        if errors:
            raise ValidationError(errors)
