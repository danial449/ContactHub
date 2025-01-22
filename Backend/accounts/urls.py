from django.urls import path
from .views import UserAccountView , ResetAccountView

urlpatterns = [
    path('<str:action>/', UserAccountView.as_view(), name='user-actions'),
    path('<str:action>/<str:token>/', UserAccountView.as_view(), name='user-actions-with-token'),
    path('<str:action>/<str:uidb64>/<str:token>/', ResetAccountView.as_view(), name='user-reset-with-token'),
]
