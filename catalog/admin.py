from django.contrib import admin
from .models import Park, Accommodation, Animal, Trip, Expedition, Customer, Feedback, DailyPlan, Itinerary
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'customer'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.

admin.site.register(Customer)
admin.site.register(Park)
admin.site.register(Accommodation)
admin.site.register(Animal)
admin.site.register(Trip)
admin.site.register(Expedition)
admin.site.register(Feedback)
admin.site.register(DailyPlan)
admin.site.register(Itinerary)
