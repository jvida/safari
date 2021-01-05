from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('parks/', views.ParkListView.as_view(), name='parks'),
    path('accommodation/', views.AccommodationListView.as_view(), name='accommodations'),
    path('expeditions/', views.ExpeditionListView.as_view(), name='expeditions'),
    path('signup/', views.create_new_user, name='signup'),
    path('profile/', views.customer_profile_view, name='profile'),
    path('profile/edit/', views.edit_user_profile, name='profile-edit'),
    path('feedbacks/', views.FeedbackListView.as_view(), name='feedbacks'),
    path('feedback/<uuid:pk>/delete/', views.FeedbackDelete.as_view(), name='feedback-delete'),
]
