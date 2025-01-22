from django.db import models
from django.contrib.auth.models import AbstractUser , User
# Create your models here.

class CustomUser(AbstractUser):

  email = models.EmailField(max_length=50 , unique=True)
  is_email_verified = models.BooleanField(default=False)
  email_verification_token = models.CharField(max_length=200 ,blank=True, null=True)

  USERNAME_FIELD = 'email'  
  REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

  def __str__(self):
    return self.first_name + " " + self.last_name