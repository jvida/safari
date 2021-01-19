from django.db import models
import calendar
import uuid
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class Animal(models.Model):
    name = models.CharField(max_length=150, help_text='Enter an animal kind (e.g. Leopard, Elephant)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=16, blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user.last_name}, {self.user.first_name}'


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular feedback.')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000, help_text='Enter your feedback.')
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(auto_now=True)


class Park(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular park.')
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, help_text='Insert where is the park located.')
    animals = models.ManyToManyField(Animal, help_text='Select animals for this park.')

    # TODO toto mozno doplnit, ale nejak rozumnejsie
    # MONTH_CHOICES = [("0", "Month doesn't matter.")] + [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    # ideal_months = models.CharField(
    #     max_length=20,
    #     choices=MONTH_CHOICES,
    #     default='0',
    #     help_text='Ideal months for visit.'
    # )

    description = models.TextField(max_length=2000, help_text='Enter a description of the park.')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Accommodation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular accommodation.')
    type = models.CharField(max_length=150, help_text='Insert an accommodation type.')
    description = models.TextField(max_length=2000, help_text='Enter a description of the accommodation type.')
    price_from = models.DecimalField(max_digits=10, decimal_places=2, help_text="Insert price from.")
    price_to = models.DecimalField(max_digits=10, decimal_places=2, help_text="Insert price to.")

    def __str__(self):
        """String for representing the Model object."""
        return self.type


class Trip(models.Model):
    park = models.ForeignKey('Park', on_delete=models.CASCADE, help_text='Select a park for this trip.')
    accommodation = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    CHOICES = [(i, i) for i in range(1, 5)]
    days = models.IntegerField(choices=CHOICES, help_text='Select how many days you wish to stay in '
                                                          'this park.')

    def __str__(self):
        """String for representing the Model object."""
        return str(self.id) + ', ' + self.park.name + ', ' + self.accommodation.type + ', ' + str(self.days)


class Expedition(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, help_text='Dont select a '
                                                                                                       'customer for '
                                                                                                       'recommended '
                                                                                                       'trips.')
    trips = models.ManyToManyField(Trip, help_text='Select trips you wish to visit.')
    CHOICES = [(i, i) for i in range(1, 10)]
    number_of_people = models.IntegerField(choices=CHOICES, blank=True, null=True, help_text='Select how many people.'
                                                                                             ' (Can be changed later)')
    message_for_us = models.TextField(max_length=2000, blank=True, help_text='Enter a message of us, if u want.')
    recommended = models.BooleanField(default=False, help_text='Is this a recommended trip by agency?')

    # def display_trips(self):
    #     """Create a string for the Trip. This is required to display trips in Admin."""
    #     return ', '.join(trip.park.name for trip in self.trips.all())

    # display_trips.short_description = 'Trips'

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}, {self.customer}, {self.number_of_people}'

    # used when adding and modifying one of recommended expeditions
    def get_absolute_url_rec(self):
        """Returns the url to access a detail record for editing of this expedition."""
        return reverse('add-recommended-expedition', args=[str(self.id)])

    # used for editing one of customer's expeditions
    def get_absolute_url_my(self):
        """Returns the url to access a detail record for editing of this expedition."""
        return reverse('edit-my-expedition', args=[str(self.id)])
