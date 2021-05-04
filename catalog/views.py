import os
from django.db.models import Sum
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .helper_functions import resize_image, expedition_helper
from PIL import Image
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from catalog.models import Park, Accommodation, Expedition, Trip, Customer, Feedback
from django.views import generic

# for user creation form
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import CreateNewUserForm, EditUserProfile, EditCustomerProfile, ExpeditionForm, BaseTripFormSet,\
    TripForm, FeedbackForm, SingleTripForm
from catalog.models import User
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.forms import modelformset_factory


# Create your views here.


def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html')


class ParkListView(generic.ListView):
    model = Park

    # I don't need this anymore, since we don't use Accommodation model for listing.
    # def get_context_data(self, **kwargs):
    #     context = super(ParkListView, self).get_context_data(**kwargs)
    #     context['accommodations'] = Accommodation.objects.all()
    #     return context


class ExpeditionListView(generic.ListView):
    model = Expedition
    template_name = 'catalog/expedition_list.html'

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs['query'] == "my_expeditions" and not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.kwargs['query'] == "recommended":
            return Expedition.objects.filter(recommended=True)
        elif self.kwargs['query'] == "my_expeditions":
            customer = Customer.objects.get(user=self.request.user)
            return Expedition.objects.filter(customer=customer)

    def get_context_data(self, **kwargs):
        context = super(ExpeditionListView, self).get_context_data(**kwargs)

        expeditions = kwargs.pop('object_list', self.object_list)
        totals = []
        for exp in expeditions:
            total_days = (Trip.objects.filter(expedition=exp)).aggregate(Sum('days'))
            totals.append(total_days['days__sum'])

        context['safaris'] = Expedition.objects.filter(recommended=True).filter(single_trip=False).exists()
        context['single_trips'] = Expedition.objects.filter(recommended=True).filter(single_trip=True).exists()
        context['query'] = self.kwargs['query']
        context['totals'] = totals
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


@login_required
def edit_user_profile(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        user_form = EditUserProfile(request.POST, instance=request.user)
        customer_form = EditCustomerProfile(request.POST, request.FILES, instance=request.user)
        # Check if forms are valid:
        if user_form.is_valid() and customer_form.is_valid():
            # process the data in forms
            phone_number = customer_form.cleaned_data['phone_number']
            customer = Customer.objects.get(user=request.user)
            customer.phone_number = phone_number

            # check if user chose a new profile picture
            # if so, it's saved
            # otherwise do nothing
            # (i have to do it this way, cause if user doesnt choose a new img, form gives the default one,
            # instead of current one)
            if request.FILES:
                picture = customer_form.cleaned_data['picture']
                # picture is resized to a square
                with Image.open(picture.file) as image:
                    picture_square = resize_image(image=image, length=700, content_file=True)
                    customer.picture.save(picture.name, picture_square)
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


@login_required
def customer_profile_view(request):
    customer = Customer.objects.get(user=request.user)
    context = {
        'customer': customer,
    }

    return render(request, 'catalog/profile.html', context)


class FeedbackListView(generic.ListView):
    model = Feedback
    ordering = ['-date_last_edit']
    paginate_by = 5


class FeedbackCreate(LoginRequiredMixin, generic.CreateView):
    model = Feedback
    success_url = reverse_lazy('feedbacks')
    # normally no need for this, but i need to specify a widget for date of trip field
    # so i get a datepicker in form
    form_class = FeedbackForm

    # this is to set the customer field to currently logged in user automatically
    def form_valid(self, form):
        form.instance.customer = Customer.objects.get(user=self.request.user)
        return super().form_valid(form)


class FeedbackUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Feedback
    success_url = reverse_lazy('feedbacks')
    # normally no need for this, but i need to specify a widget for date of trip field
    # so i get a datepicker in form
    form_class = FeedbackForm


class FeedbackDelete(LoginRequiredMixin, generic.DeleteView):
    model = Feedback
    success_url = reverse_lazy('feedbacks')


@login_required
def create_new_expedition(request, exp_type):
    print("add_recommended_expedition", exp_type)
    num_parks, trip_form, single_trip = expedition_helper(exp_type)
    TripFormSet = modelformset_factory(Trip, form=trip_form, formset=BaseTripFormSet,
                                       max_num=num_parks, min_num=1, extra=0, validate_min=True)
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        trip_formset = TripFormSet(request.POST)
        expedition_form = ExpeditionForm(request.POST)

        # Check if the form is valid:
        if expedition_form.is_valid() and trip_formset.is_valid():
            # process the data in form.cleaned_data as required
            expedition = expedition_form.save()
            trips = trip_formset.save(
                commit=False)  # i dont want to save all trips, because i dont want duplicates in DB
            # for trip in trips:
            for trip in trips:
                """Check if this trip already exists in DB"""
                trip, created = Trip.objects.get_or_create(park=trip.park,
                                                           accommodation=trip.accommodation,
                                                           days=trip.days)
                expedition.trips.add(trip)

            expedition.customer = Customer.objects.get(user=request.user)
            expedition.single_trip = single_trip
            expedition.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('expeditions', args=("my_expeditions",)))
        # # If this is a GET (or any other method) create the default form.
    else:
        expedition_form = ExpeditionForm()
        # By default, when you create a formset from a model, the formset will use a queryset
        # that includes all objects in the model (e.g., Author.objects.all()).
        # You can override this behavior by using the queryset argument:
        trip_formset = TripFormSet(queryset=Trip.objects.none())

    context = {
        'trip_formset': trip_formset,
        'expedition_form': expedition_form,
    }
    return render(request, 'catalog/create_expedition.html', context)


@login_required
def add_recommended_expedition(request, pk, exp_type):
    print("add_recommended_expedition", exp_type)
    num_parks, trip_form, single_trip = expedition_helper(exp_type)
    TripFormSet = modelformset_factory(Trip, form=trip_form, formset=BaseTripFormSet,
                                       max_num=num_parks, min_num=1, extra=0, validate_min=True)
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        trip_formset = TripFormSet(request.POST)
        expedition_form = ExpeditionForm(request.POST)

        # Check if the form is valid:
        if expedition_form.is_valid() and trip_formset.is_valid():
            # process the data in form.cleaned_data as required
            expedition = expedition_form.save()
            trips = trip_formset.save(
                commit=False)  # i dont want to save all trips, because i dont want duplicates in DB
            # for trip in trips:
            print(trips)
            for trip in trips:
                """Check if this trip already exists in DB"""
                trip, created = Trip.objects.get_or_create(park=trip.park,
                                                           accommodation=trip.accommodation,
                                                           days=trip.days)
                print(trip)
                expedition.trips.add(trip)

            expedition.customer = Customer.objects.get(user=request.user)
            expedition.single_trip = single_trip
            expedition.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('expeditions', args=("my_expeditions",)))
        # # If this is a GET (or any other method) create the default form.
    else:
        expedition_form = ExpeditionForm(instance=Expedition.objects.get(id=pk))
        trip_formset = TripFormSet(queryset=Expedition.objects.get(id=pk).trips.all())

    context = {
        'trip_formset': trip_formset,
        'expedition_form': expedition_form,
    }
    return render(request, 'catalog/create_expedition.html', context)


@login_required
def edit_my_expedition(request, pk, exp_type):
    print("edit_my_expedition", exp_type)
    num_parks, trip_form, single_trip = expedition_helper(exp_type)
    TripFormSet = modelformset_factory(Trip, form=trip_form, formset=BaseTripFormSet,
                                       max_num=num_parks, min_num=1, extra=0, validate_min=True)

    expedition_instance = get_object_or_404(Expedition, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        trip_formset = TripFormSet(request.POST)
        expedition_form = ExpeditionForm(request.POST)

        # Check if the form is valid:
        if expedition_form.is_valid() and trip_formset.is_valid():
            # process the data in form.cleaned_data as required

            expedition_instance.number_of_people = expedition_form.cleaned_data['number_of_people']
            expedition_instance.message_for_us = expedition_form.cleaned_data['message_for_us']
            expedition_instance.date_from = expedition_form.cleaned_data['date_from']
            expedition_instance.date_to = expedition_form.cleaned_data['date_to']
            expedition_instance.trips.clear()

            trips = trip_formset.save(
                commit=False)  # i dont want to save all trips, because i dont want duplicates in DB
            # for trip in trips:
            for trip in trips:
                """Check if this trip already exists in DB"""
                trip, created = Trip.objects.get_or_create(park=trip.park,
                                                           accommodation=trip.accommodation,
                                                           days=trip.days)
                print(trip)
                expedition_instance.trips.add(trip)
            expedition_instance.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('expeditions', args=("my_expeditions",)))
        # # If this is a GET (or any other method) create the default form.
    else:
        expedition_form = ExpeditionForm(instance=Expedition.objects.get(id=pk))
        trip_formset = TripFormSet(queryset=Expedition.objects.get(id=pk).trips.all())

    context = {
        'trip_formset': trip_formset,
        'expedition_form': expedition_form,
    }
    return render(request, 'catalog/create_expedition.html', context)


class ExpeditionDelete(LoginRequiredMixin, generic.DeleteView):
    model = Expedition
    success_url = reverse_lazy('expeditions', kwargs={'query': "my_expeditions"})


def about_us(request):
    """View function for about us page of site."""

    # Render the HTML template catalog/about_us.html with the data in the context variable
    return render(request, 'catalog/about_us.html')


def gallery(request):
    """View function for home page of site."""

    context = {}
    # files = os.listdir(os.path.join(settings.STATIC_ROOT, "img/gallery/"))
    # gallery_images = os.listdir('catalog/static/img/gallery/')   # TODO toto mozno este nejako upravit rozumnejsie
    gallery_images = os.listdir('/home/drozdo/safari/catalog/static/img/gallery/')
    context['images'] = gallery_images

    # Render the HTML template catalog/gallery.html with the data in the context variable
    return render(request, 'catalog/gallery.html', context)
