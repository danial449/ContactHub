from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer
from .hubspot_service import HubSpotService
from rest_framework.permissions import AllowAny, IsAuthenticated

class ContactListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Fetch contacts from HubSpot
        hubspot_contacts = HubSpotService.get_all_contacts()
        # Optional: Sync with local database
        for contact in hubspot_contacts:
            identity_profile = contact['identity-profiles'][0] if contact['identity-profiles'] else None

            # Proceed if there is a valid identity profile
            if identity_profile:
                email = None
                for identity in identity_profile['identities']:
                    if identity['type'] == 'EMAIL':
                        email = identity['value']
                        break 
                    
            Contact.objects.update_or_create(
                hubspot_id=contact['vid'],
                defaults={
                    'first_name': contact['properties']['firstname']['value'],
                    'last_name': contact['properties']['lastname']['value'],
                    'email': email
                },
            )
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            # Create contact on HubSpot
            hubspot_data = {
                "properties": [
                    {"property": "firstname", "value": serializer.validated_data['first_name']},
                    {"property": "lastname", "value": serializer.validated_data['last_name']},
                    {"property": "email", "value": serializer.validated_data['email']},
                ]
            }
            hubspot_response = HubSpotService.create_contact(hubspot_data)
            serializer.save(hubspot_id=hubspot_response['vid'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactDetailView(APIView):
    def put(self, request, pk):
        contact = Contact.objects.get(pk=pk)
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            # Update contact on HubSpot
            hubspot_data = {
                "properties": [
                    {"property": "firstname", "value": serializer.validated_data['first_name']},
                    {"property": "lastname", "value": serializer.validated_data['last_name']},
                    {"property": "email", "value": serializer.validated_data['email']},
                ]
            }
            HubSpotService.update_contact(contact.hubspot_id, hubspot_data)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contact = Contact.objects.get(pk=pk)
        # Delete contact on HubSpot
        HubSpotService.delete_contact(contact.hubspot_id)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
