from django.db import models

class Contact(models.Model):
    hubspot_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    website = models.CharField(max_length=255 , null=True , blank=True)
    company = models.CharField(max_length=255 , null=True , blank=True)
    address = models.CharField(max_length=255 , null=True , blank=True)
    state = models.CharField(max_length=255 , null=True , blank=True)
    phone = models.CharField(max_length=255 , null=True , blank=True)
    zip = models.CharField(max_length=255 , null=True , blank=True)
    email = models.EmailField(unique=True, null=True , blank=True)
    added_at = models.DateField(null=True , blank=True, auto_now_add=True)
    lastmodifieddate = models.DateField(null=True , blank=True, auto_now=True)

    def __str__(self):
        return self.first_name
