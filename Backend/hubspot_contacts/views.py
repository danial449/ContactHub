from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer
from .hubspot_service import HubSpotService
from rest_framework.permissions import IsAuthenticated
from datetime import datetime


class ContactListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all contacts and sync with the local database."""
        hubspot_contacts = HubSpotService.get_all_contacts()
        for contact in hubspot_contacts:
            identity_profile = contact['identity-profiles'][0] if contact['identity-profiles'] else None
            if identity_profile:
                email = next(
                    (identity['value'] for identity in identity_profile['identities'] if identity['type'] == 'EMAIL'),
                    None,
                )
                added_at_timestamp = contact.get('addedAt')
                modified_at_timestamp = contact['properties']['lastmodifieddate']['value']

                added_at = datetime.fromtimestamp(added_at_timestamp / 1000) if added_at_timestamp else None
                lastmodifieddate = datetime.fromtimestamp(int(modified_at_timestamp) / 1000) if modified_at_timestamp else None

                Contact.objects.update_or_create(
                    hubspot_id=contact['vid'],
                    defaults={
                        'first_name': contact['properties'].get('firstname', {}).get('value', ''),
                        'last_name': contact['properties'].get('lastname', {}).get('value', ''),
                        'company': contact['properties'].get('company', {}).get('value', ''),
                        'website': contact['properties'].get('website', {}).get('value', ''),
                        'phone': contact['properties'].get('phone', {}).get('value', ''),
                        'address': contact['properties'].get('address', {}).get('value', ''),
                        'state': contact['properties'].get('state', {}).get('value', ''),
                        'zip': contact['properties'].get('zip', {}).get('value', ''),
                        'email': email,
                        'added_at': added_at,
                        'lastmodifieddate': lastmodifieddate,
                        },
                )
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new contact."""
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            hubspot_data = {
                "properties": [
                    {"property": "firstname", "value": serializer.validated_data.get('first_name', '')},
                    {"property": "lastname", "value": serializer.validated_data.get('last_name', '')},
                    {"property": "email", "value": serializer.validated_data.get('email', '')},
                    {"property": "company", "value": serializer.validated_data.get('company', '')},
                    {"property": "website", "value": serializer.validated_data.get('website', '')},
                    {"property": "phone", "value": serializer.validated_data.get('phone', '')},
                    {"property": "address", "value": serializer.validated_data.get('address', '')},
                    {"property": "state", "value": serializer.validated_data.get('state', '')},
                    {"property": "zip", "value": serializer.validated_data.get('zip', '')},
            ]
            }
            hubspot_response = HubSpotService.create_contact(hubspot_data)
            serializer.save(hubspot_id=hubspot_response['vid'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetailView(APIView):
    def get(self, request, pk):
        contact = Contact.objects.get(pk=pk)
        serializer = ContactSerializer(contact)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """Update an existing contact."""
        contact = Contact.objects.get(pk=pk)
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            hubspot_data = {
                "properties": [
                    {"property": "firstname", "value": serializer.validated_data.get('first_name', '')},
                    {"property": "lastname", "value": serializer.validated_data.get('last_name', '')},
                    {"property": "email", "value": serializer.validated_data.get('email', '')},
                    {"property": "company", "value": serializer.validated_data.get('company', '')},
                    {"property": "website", "value": serializer.validated_data.get('website', '')},
                    {"property": "phone", "value": serializer.validated_data.get('phone', '')},
                    {"property": "address", "value": serializer.validated_data.get('address', '')},
                    {"property": "state", "value": serializer.validated_data.get('state', '')},
                    {"property": "zip", "value": serializer.validated_data.get('zip', '')},
                ]
            }
            HubSpotService.update_contact(contact.hubspot_id, hubspot_data)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a contact."""
        contact = Contact.objects.get(pk=pk)
        HubSpotService.delete_contact(contact.hubspot_id)
        contact.delete()
        return Response("Contact Deleted Successfully",status=status.HTTP_204_NO_CONTENT)


class HubSpotAdvancedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, action):
        """Handle advanced HubSpot services."""
        if action == 'recently_updated':
            contacts = HubSpotService.get_recently_updated_contacts()
        elif action == 'recently_created':
            contacts = HubSpotService.get_recently_created_contacts()
        elif action == 'lifecycle_metrics':
            contacts = HubSpotService.get_lifecycle_stage_metrics()
        elif action == 'contact_statistics':
            contacts = HubSpotService.get_contact_statistics()
        elif action == 'search':
            query = request.query_params.get('q', '')
            contacts = HubSpotService.search_contacts(query)
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(contacts, status=status.HTTP_200_OK)

