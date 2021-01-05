from django.shortcuts import render, get_object_or_404
from catalog.models import Park, Accommodation, Expedition, Trip, Customer
from django.views import generic

# for user creation form
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import CreateNewUserForm, EditUserProfile, EditCustomerProfile
from catalog.models import User
from django.contrib.auth import login
from django.contrib.auth.models import Group


# Create your views here.


def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html')


class ParkListView(generic.ListView):
    model = Park

    def get_context_data(self, **kwargs):
        context = super(ParkListView, self).get_context_data(**kwargs)
        context['accommodations'] = Accommodation.objects.all()
        return context


class AccommodationListView(generic.ListView):
    model = Accommodation


class ExpeditionListView(generic.ListView):
    model = Expedition
    queryset = Expedition.objects.filter(recommended=True)

    def get_context_data(self, **kwargs):
        context = super(ExpeditionListView, self).get_context_data(**kwargs)
        context['trips'] = Trip.objects.all()
        return context


def create_new_user(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = CreateNewUserForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            pswd = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']

            customer = Customer()
            customer.user = User.objects.create_user(username, email, pswd, first_name=first_name, last_name=last_name)
            customer.phone_number = phone_number
            customer.save()

            group = Group.objects.get(name='Customers')
            customer.user.groups.add(group)
            # login(request, user) # toto ak by som chcel rovno aj lognut. potom redirect to 'index'
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('login'))
        # # If this is a GET (or any other method) create the default form.
    else:
        form = CreateNewUserForm()

    context = {
        'form': form,
    }

    return render(request, 'catalog/sign_up.html', context)


def edit_user_profile(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        user_form = EditUserProfile(request.POST, instance=request.user)
        customer_form = EditCustomerProfile(request.POST, instance=request.user)
        # Check if forms are valid:
        if user_form.is_valid() and customer_form.is_valid():
            # process the data in forms
            phone_number = customer_form.cleaned_data['phone_number']
            customer = Customer.objects.get(user=request.user)
            customer.phone_number = phone_number
            user_form.save()
            customer.save()
            return HttpResponseRedirect(reverse('profile'))
    # else it's a GET request so show data
    else:
        customer = Customer.objects.get(user=request.user)
        user_form = EditUserProfile(instance=request.user)
        customer_form = EditCustomerProfile(instance=customer)

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
    }

    return render(request, 'catalog/profile_edit.html', context)


def customer_profile_view(request):
    customer = Customer.objects.get(user=request.user)
    context = {
        'customer': customer,
    }

    return render(request, 'catalog/profile.html', context)


