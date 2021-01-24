import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import timedelta

import datetime

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event

EVENT_URL = reverse('event:event-list')

def detail_url(event_id):
    """Return event detail URL"""
    return reverse('event:event-detail', args=[event_id])

def sample_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)

def sample_event(
    organizer,
    title='test title',
    description='test description',
    event_time=make_aware(datetime.datetime.now()),
    address='test address',
    fee=500
    ):

    """Create and return a sample event"""
    default = {
        'title': title,
        'description': description,
        'organizer': organizer,
        'image': '',
        'event_time': event_time.strftime('%Y-%m-%d %H:%M:%S'),
        'address': address,
        'fee': fee,
    }
    return Event.objects.create(**default)

def get_event_by_json(**params):
    event = Event.objects.get(
        organizer=params['organizer'],
        event_time=params['event_time'],
    )

    expected_json_dict = {
        'title': event.title,
        'description': event.description,
        'organizer': event.organizer,
        'image': event.image,
        'event_time': event.event_time,
        'address': event.address,
        'fee': event.fee,
        'is_active': event.is_active
    }

    return expected_json_dict

class PublicParticipantApiTests(TestCase):
    """Test that publcly available participant API"""

    def setUp(self):
        self.organizer = sample_user(
            email='testorganaizer@matsuda.com',
            password='testpass'
        )
        self.first_event = sample_event(organizer=self.organizer)
        self.second_event = sample_event(
            organizer=self.organizer,
            title='second event title',
            event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=1)),
            description='second event description',
            address='second event address',
            fee='700'
        )
        self.client = APIClient()


    def test_retrieve_event_list_success(self):
        """Test retrieving event list"""
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'start':today, 'end':tomorrow})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict_list = [
            {
                'id': self.first_event.id,
                'title': self.first_event.title,
                'image': self.first_event.get_image_url,
                'event_time': self.first_event.event_time,
                'address': self.first_event.address,
                'participant_count': 0
            },{
                'id': self.second_event.id,
                'title': self.second_event.title,
                'image': self.second_event.get_image_url,
                'event_time': self.second_event.event_time,
                'address': self.second_event.address,
                'participant_count': 0
            }
        ]
        expected_json = {
            "count":2,
            "next":None,
            "previous":None,
            "results":expected_json_dict_list
        }
        self.assertJSONEqual(res.content, expected_json)

    def test_retrieve_event_pagination_success(self):
        """Test retrieving event with pagination"""
        count= 0
        while count < 30:
            sample_event(organizer=self.organizer)
            count += 1

        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'start':today, 'end':tomorrow})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 30)

        res = self.client.get(EVENT_URL, {'start':today, 'end':tomorrow, 'page':2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_retrieving_events_for_a_day_successful(self):
        """Test retrieving events for a day"""
        sample_event(
            organizer=self.organizer,
            event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=2))
        )
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'start':today, 'end':tomorrow})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_not_retrieving_events_by_wrong_query_parameters_name(self):
        """Test not retrieving events by wrong query parameter name"""
        sample_event(
            organizer=self.organizer,
            event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=2))
        )
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'test':today, 'test':tomorrow})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_retrieving_events_by_wrong_type_query_parameters(self):
        """Test not retrieving events by wrong type query parameters"""
        sample_event(
            organizer=self.organizer,
            event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=2))
        )
        res = self.client.get(EVENT_URL, {'start':'test', 'end':'test'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_retrieving_events_by_wrong_query_parameters_number(self):
        """Test not retrieving events by wrong query parameters number"""
        sample_event(
            organizer=self.organizer,
            event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=2))
        )
        today = datetime.date.today()
        res = self.client.get(EVENT_URL, {'start':today})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_event_success(self):
        """Test retrieving event"""
        url = detail_url(self.second_event.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        event = Event.objects.get(id=self.second_event.id)
        organizer = get_user_model().objects.get(id=event.organizer_id)
        expected_json_dict = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'organizer': event.organizer_id,
            'organizer_first_name': organizer.first_name,
            'organizer_icon': organizer.get_icon_url,
            'image': event.get_image_url,
            'event_time': event.get_brief_event_time,
            'address': event.address,
            'fee': event.fee,
            'status': event.status,
            'brief_updated_at': event.get_brief_updated_at
        }
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_create_event_for_unauthorized_user(self):
        """Test false creating a new event"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'image': '',
            'organizer_id': self.organizer.id,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': 500,
        }
        res = self.client.post(EVENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event_for_unauthorized_user(self):
        """Test false logically deleting an event for not authenticated user"""
        url = detail_url(self.first_event.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_event_for_unauthorized_user(self):
        """Test false updating an event for not authenticated user"""
        payload = {
            'title': 'test update title',
            'description': 'test update description',
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test update address',
            'fee': '600',
        }
        url = detail_url(self.first_event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateParticipantApiTests(TestCase):
    """Test the authorized user event API"""

    def setUp(self):
        self.client = APIClient()
        self.organizer = sample_user(
            email='testorganizer@matsuda.com',
            password='testpass'
        )
        self.organizer.is_guide = True
        self.organizer.save()
        self.user_one = sample_user(
            email='testone@matsuda.com',
            password='testpass'
        )

        self.event = sample_event(self.organizer)

        self.client.force_authenticate(self.organizer)

    def test_create_event_successful(self):
        """Test create a new event"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test address',
            'fee': 500,
            'status': '1'
        }
        res = self.client.post(EVENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_not_creating_event_by_tourist(self):
        """Test not creating a new event by tourist"""
        self.client.force_authenticate(self.user_one)
        payload = {
            'title': 'test title',
            'description': 'test description',
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test address',
            'fee': 500,
            'status': '1'
        }
        res = self.client.post(EVENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_logically_delete_event(self):
        """Test logically delete an event for authenticated user"""
        url = detail_url(self.event.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.event.refresh_from_db()

        self.assertFalse(self.event.is_active)

    def test_false_logically_deleting_event_for_not_organizer(self):
        """Test false logically deleting an event for not organizer"""
        self.client.force_authenticate(self.user_one)
        url = detail_url(self.event.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_event_successful(self):
        """Test updating an event successful"""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            payload = {
                'title': 'test update title',
                'description': 'test update description',
                'image': ntf,
                'event_time': make_aware(datetime.datetime.now()),
                'address': 'test update address',
                'fee': '600',
                'status': '2'
            }
            url = detail_url(self.event.id)
            res = self.client.patch(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.event.image.delete()

    def test_false_updating_event_for_anyone(self):
        """Test false updating an event for not organizer"""
        self.client.force_authenticate(self.user_one)
        payload = {
            'title': 'test update title',
            'description': 'test update description',
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test update address',
            'fee': '600',
            'status': '2'
        }
        url = detail_url(self.event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
