from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('parks/', views.ParkListView.as_view(), name='parks'),
    path('accommodation/', views.AccommodationListView.as_view(), name='accommodations'),
    path('expeditions/', views.ExpeditionListView.as_view(), name='expeditions'),
]
