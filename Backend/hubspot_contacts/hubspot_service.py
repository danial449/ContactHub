import requests
import os
from dotenv import load_dotenv


class HubSpotService:
    BASE_URL = "https://api.hubapi.com/contacts/v1"
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv('HUBSPOT_API_KEY')

    if not api_key:
        raise ValueError("HubSpot API key not found. Please set HUBSPOT_API_KEY in your .env file.")

    HEADERS = {"Authorization": f"Bearer {api_key}"}

    @staticmethod
    def get_all_contacts():
        endpoint = f"{HubSpotService.BASE_URL}/lists/all/contacts/all"
        response = requests.get(endpoint, headers=HubSpotService.HEADERS)
        if response.status_code == 200:
            return response.json().get("contacts", [])
        response.raise_for_status()
        
    @staticmethod
    def get_recently_updated_contacts(count=100):
        endpoint = f"{HubSpotService.BASE_URL}/lists/recently_updated/contacts/recent"
        params = {"count": count}
        response = requests.get(endpoint, headers=HubSpotService.HEADERS, params=params)
        if response.status_code == 200:
            return response.json().get("contacts", [])
        response.raise_for_status()

    @staticmethod
    def get_recently_created_contacts(count=100):
        endpoint = f"{HubSpotService.BASE_URL}/lists/all/contacts/recent"
        params = {"count": count}
        response = requests.get(endpoint, headers=HubSpotService.HEADERS, params=params)
        if response.status_code == 200:
            return response.json().get("contacts", [])
        response.raise_for_status()

    @staticmethod
    def get_contact_by_vid(contact_id):
        endpoint = f"{HubSpotService.BASE_URL}/contact/vid/{contact_id}/profile"
        response = requests.get(endpoint, headers=HubSpotService.HEADERS)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    @staticmethod
    def get_contacts_by_vids(contact_ids):
        endpoint = f"{HubSpotService.BASE_URL}/contact/vids/batch"
        params = {"vid": contact_ids}
        response = requests.get(endpoint, headers=HubSpotService.HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()



    @staticmethod
    def get_contacts_by_emails(emails):
        endpoint = f"{HubSpotService.BASE_URL}/contact/emails/batch"
        params = {"email": emails}
        response = requests.get(endpoint, headers=HubSpotService.HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    @staticmethod
    def get_lifecycle_stage_metrics():
        endpoint = f"{HubSpotService.BASE_URL}/lists/static"
        response = requests.get(endpoint, headers=HubSpotService.HEADERS)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    @staticmethod
    def get_contact_statistics():
        endpoint = f"{HubSpotService.BASE_URL}/contacts/statistics"
        response = requests.get(endpoint, headers=HubSpotService.HEADERS)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    @staticmethod
    def search_contacts(query):
        endpoint = f"{HubSpotService.BASE_URL}/search/query"
        params = {"q": query}
        response = requests.get(endpoint, headers=HubSpotService.HEADERS, params=params)
        if response.status_code == 200:
            return response.json().get("contacts", [])
        response.raise_for_status()

    @staticmethod
    def create_contact(data):
        endpoint = f"{HubSpotService.BASE_URL}/contact"
        response = requests.post(endpoint, json=data, headers=HubSpotService.HEADERS)
        if response.status_code == 200:
            return response.json()
        response.raise_for_status()

    @staticmethod
    def update_contact(contact_id, data):
        endpoint = f"{HubSpotService.BASE_URL}/contact/vid/{contact_id}/profile"
        response = requests.post(endpoint, json=data, headers=HubSpotService.HEADERS)
        if response.status_code == 204:
            return {"message": "Contact updated successfully"}
        response.raise_for_status()


    @staticmethod
    def delete_contact(contact_id):
        endpoint = f"{HubSpotService.BASE_URL}/contact/vid/{contact_id}"
        response = requests.delete(endpoint, headers=HubSpotService.HEADERS)
        if response.status_code == 200:
            return {"message": "Contact deleted successfully"}
        response.raise_for_status()
