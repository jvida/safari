from django.shortcuts import render
from catalog.models import Park, Accommodation
from django.views import generic

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

