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
    phone_number = models.CharField(max_length=16, blank=True,
                                    help_text='Enter your phone number in international format. (e.g. +421944123132)')
    picture = models.ImageField(upload_to='profile_imgs/', default='profile_imgs/anonymous-user.png')
    hidden_email = models.BooleanField(default=False)
    hidden_phone = models.BooleanField(default=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.user.username} ({self.user.last_name}, {self.user.first_name})'


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular feedback.')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000, help_text='Enter your feedback.')
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_edit = models.DateTimeField(auto_now=True)
    date_of_trip = models.DateField(blank=False)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.customer}, {self.date_created.date()}'


class Park(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular park.')
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, help_text='Insert where is the park located.')
    animals = models.ManyToManyField(Animal, help_text='Select animals for this park.')
    picture = models.ImageField(upload_to='park_imgs/', help_text='Upload an image.')
    safari = models.BooleanField()

    # TODO toto mozno doplnit, ale nejak rozumnejsie
    # MONTH_CHOICES = [("0", "Month doesn't matter.")] + [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    # ideal_months = models.CharField(
    #     max_length=20,
    #     choices=MONTH_CHOICES,
    #     default='0',
    #     help_text='Ideal months for visit.'
    # )

    description = models.TextField(max_length=5000, help_text='Enter a description of the park.')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Accommodation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular accommodation.')
    type = models.CharField(max_length=150, help_text='Insert an accommodation type.')
    description = models.TextField(max_length=2000, help_text='Enter a description of the accommodation type.',
                                   blank=True)
    price_from = models.DecimalField(max_digits=10, decimal_places=2, help_text="Insert price from.", blank=True,
                                     null=True)
    price_to = models.DecimalField(max_digits=10, decimal_places=2, help_text="Insert price to.", blank=True, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.type


class Trip(models.Model):
    park = models.ForeignKey('Park', on_delete=models.CASCADE, help_text='Select a park for this trip.')
    accommodation = models.ForeignKey('Accommodation', on_delete=models.CASCADE,
                                      help_text='Select what accommodation you prefer.')
    CHOICES = [(i, i) for i in range(1, 10)]
    days = models.IntegerField(choices=CHOICES, help_text='Select how many days you wish to stay in '
                                                          'this park.')
    days_up_to = models.IntegerField(choices=CHOICES, help_text='Select up to how many days.', blank=True, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return str(self.id) + ', ' + self.park.name + ', ' + self.accommodation.type + ', ' + str(self.days)


class DailyPlan(models.Model):
    label = models.CharField(max_length=150, help_text='Enter an identification for this day. (e.g. 5-day: Day 1)')
    title = models.CharField(max_length=150, help_text='Enter a short description for this day. (e.g. Day 1: Arusha)')
    description = models.TextField(max_length=2000, help_text='Enter a programme for this day.')

    def __str__(self):
        """String for representing the Model object."""
        return self.label


class Itinerary(models.Model):
    name = models.CharField(max_length=150,
                            help_text='Enter some name for easier organization. (e.g. 5-day safari itinerary)')
    dailyPlans = models.ManyToManyField('DailyPlan', help_text='Select daily plans.', blank=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Expedition(models.Model):
    name = models.CharField(max_length=150, blank=True,
                            help_text='Enter a name for this recommended expedition. (e.g. 5-day safari)')
    tag = models.CharField(max_length=50, blank=True,
                           help_text='Enter a tag for this recommended expedition. (e.g. 5day)')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, help_text='Dont select a '
                                                                                                       'customer for '
                                                                                                       'recommended '
                                                                                                       'trips.')
    trips = models.ManyToManyField(Trip, help_text='Select safari trips you wish to visit.')
    CHOICES = [(i, i) for i in range(1, 10)]
    number_of_people = models.IntegerField(choices=CHOICES, blank=True, null=True, help_text='Select how many people.')
    message_for_us = models.TextField(max_length=2000, blank=True, help_text='Enter a message for us, if u want.')
    recommended = models.BooleanField(default=False, help_text='Is this a recommended trip by agency?')
    single_trip = models.BooleanField(null=True)
    sent = models.BooleanField(default=False)
    description = models.TextField(max_length=2000, blank=True,
                                   help_text='Enter a short description for this expedition.')
    itinerary = models.ForeignKey('Itinerary', on_delete=models.CASCADE, blank=True, null=True)
    date_from = models.DateField(blank=True, null=True,
                                 help_text='Select a time window in which You wish to join us for an advanture.')
    date_to = models.DateField(blank=True, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}, {self.name}, {self.customer}, {self.number_of_people}, recommended: {self.recommended}, ' \
               f'sent: {self.sent} '

    # used when adding and modifying one of recommended expeditions
    def get_absolute_url_rec(self):
        """Returns the url to access a detail record for editing of this expedition."""
        return reverse('add-recommended-expedition', kwargs={'pk': str(self.id),
                                                             'exp_type': "safari"}, )

    # used when adding and modifying one of recommended single trip expeditions
    def get_absolute_url_rec_single(self):
        """Returns the url to access a detail record for editing of this expedition."""
        return reverse('add-recommended-expedition', kwargs={'pk': str(self.id),
                                                             'exp_type': "single_trip"}, )

    # used when modifying my expeditions
    def get_absolute_url_my(self):
        """Returns the url to access a detail record for editing of this expedition."""
        return reverse('edit-my-expedition', kwargs={'pk': str(self.id),
                                                     'exp_type': "safari"}, )

    # used when modifying my single trip expeditions
    def get_absolute_url_my_single(self):
        """Returns the url to access a detail record for editing of this expedition."""
        return reverse('edit-my-expedition', kwargs={'pk': str(self.id),
                                                     'exp_type': "single_trip"}, )
