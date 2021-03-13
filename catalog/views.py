import os

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from catalog.models import Park, Accommodation, Expedition, Trip, Customer, Feedback
from django.views import generic

# for user creation form
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import CreateNewUserForm, EditUserProfile, EditCustomerProfile, ExpeditionForm, BaseTripFormSet, TripForm
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

    def get_context_data(self, **kwargs):
        context = super(ParkListView, self).get_context_data(**kwargs)
        context['accommodations'] = Accommodation.objects.all()
        return context


# class AccommodationListView(generic.ListView):
#     model = Accommodation


class ExpeditionListView(generic.ListView):
    model = Expedition
    template_name = 'catalog/expedition_list.html'

    def get_queryset(self):
        if self.kwargs['query'] == "recommended":
            return Expedition.objects.filter(recommended=True)
        elif self.kwargs['query'] == "my_expeditions":
            customer = Customer.objects.get(user=self.request.user)
            return Expedition.objects.filter(customer=customer)

    def get_context_data(self, **kwargs):
        context = super(ExpeditionListView, self).get_context_data(**kwargs)
        context['trips'] = Trip.objects.all()
        context['query'] = self.kwargs['query']
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


class FeedbackListView(generic.ListView):
    model = Feedback


class FeedbackCreate(generic.CreateView):
    model = Feedback
    fields = ['content']
    success_url = reverse_lazy('feedbacks')

    # this is to set the customer field to currently logged in user automatically
    def form_valid(self, form):
        form.instance.customer = Customer.objects.get(user=self.request.user)
        return super().form_valid(form)


class FeedbackUpdate(generic.UpdateView):
    model = Feedback
    fields = ['content']
    success_url = reverse_lazy('feedbacks')


class FeedbackDelete(generic.DeleteView):
    model = Feedback
    success_url = reverse_lazy('feedbacks')


def create_new_expedition(request):
    num_parks = Park.objects.all().count()
    TripFormSet = modelformset_factory(Trip, form=TripForm, formset=BaseTripFormSet,
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


def add_recommended_expedition(request, pk):
    print("add_recommended_expedition")
    num_parks = Park.objects.all().count()
    TripFormSet = modelformset_factory(Trip, form=TripForm, formset=BaseTripFormSet,
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


def edit_my_expedition(request, pk):
    print("edit_my_expedition")
    num_parks = Park.objects.all().count()
    TripFormSet = modelformset_factory(Trip, form=TripForm, formset=BaseTripFormSet,
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


class ExpeditionDelete(generic.DeleteView):
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
    gallery_images = os.listdir('catalog/static/img/gallery/')   # TODO toto mozno este nejako upravit rozumnejsie
    context['images'] = gallery_images

    # Render the HTML template catalog/gallery.html with the data in the context variable
    return render(request, 'catalog/gallery.html', context)
