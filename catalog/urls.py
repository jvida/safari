from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('parks/', views.ParkListView.as_view(), name='parks'),
    # path('accommodation/', views.AccommodationListView.as_view(), name='accommodations'),
    path('expeditions/<str:query>/', views.ExpeditionListView.as_view(), name='expeditions'),
    path('signup/', views.create_new_user, name='signup'),
    path('profile/', views.customer_profile_view, name='profile'),
    path('profile/edit/', views.edit_user_profile, name='profile-edit'),
    path('feedbacks/', views.FeedbackListView.as_view(), name='feedbacks'),
    path('feedback/create/', views.FeedbackCreate.as_view(), name='feedback-create'),
    path('feedback/<uuid:pk>/update/', views.FeedbackUpdate.as_view(), name='feedback-update'),
    path('feedback/<uuid:pk>/delete/', views.FeedbackDelete.as_view(), name='feedback-delete'),
    path('expedition/<str:exp_type>/create/', views.create_new_expedition, name='create-expedition'),
    path('expedition/<int:pk>/<str:exp_type>/add/', views.add_recommended_expedition, name='add-recommended-expedition'),
    path('expedition/<int:pk>/<str:exp_type>/edit/', views.edit_my_expedition, name='edit-my-expedition'),
    path('expedition/<int:pk>/delete/', views.ExpeditionDelete.as_view(), name='expedition-delete'),
    path('about-us/', views.about_us, name='about-us'),
    path('gallery/', views.gallery, name='gallery'),
]
