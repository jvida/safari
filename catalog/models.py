from django.db import models
import calendar
import uuid


# Create your models here.
class Animal(models.Model):
    name = models.CharField(max_length=150, help_text='Enter an animal kind (e.g. Leopard, Elephant)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Park(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular park.')
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=150, help_text='Insert where is the park located.')
    animals = models.ManyToManyField(Animal, help_text='Select animals for this park.')

    MONTH_CHOICES = [("0", "Month doesn't matter.")] + [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    ideal_months = models.CharField(
        max_length=20,
        choices=MONTH_CHOICES,
        default='0',
        help_text='Ideal months for visit.'
    )

    description = models.TextField(max_length=2000, help_text='Enter a description of the park.')

    def __str__(self):
        """String for representing the Model object."""
        return self.name


class Accommodation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular accommodation.')
    type = models.CharField(max_length=150, help_text='Insert an accommodation type.')
    description = models.TextField(max_length=2000, help_text='Enter a description of the accommodation type.')
    price_from = models.DecimalField(max_digits=10, decimal_places=2, help_text="Insert price from.")
    price_to = models.DecimalField(max_digits=10, decimal_places=2, help_text="Insert price to.")

    def __str__(self):
        """String for representing the Model object."""
        return self.type

