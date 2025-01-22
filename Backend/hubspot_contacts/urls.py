from django.urls import path
from .views import ContactListView, ContactDetailView, HubSpotAdvancedView

urlpatterns = [
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('hubspot/<str:action>/', HubSpotAdvancedView.as_view(), name='hubspot-advanced'),
]
