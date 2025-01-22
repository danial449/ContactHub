from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'company', 'website', 'phone', 'address', 'state', 'zip', 'email','added_at' , 'lastmodifieddate']
