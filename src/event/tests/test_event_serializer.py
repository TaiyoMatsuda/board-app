from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware, localtime
import datetime

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event

from event.serializers import EventSerializer

def sample_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)

def sample_event(user):
    """Create and return a sample comment"""
    default = {
        'title': 'test title',
        'description': 'test description',
        'organizer': user,
        'image': '',
        'event_time': make_aware(datetime.datetime.now())
        .strftime('%Y-%m-%d %H:%M:%S'),
        'address': 'test address',
        'fee': 500,
    }

    return Event.objects.create(**default)


class PrivateEventApiTests(TestCase):
    """Test the authorized user Event API"""

    def setUp(self):
        self.client = APIClient()
        self.organizer = sample_user(
            email='organizer@matsuda.com',
            password='testpass'
        )
        self.event = sample_event(self.organizer)

        self.client.force_authenticate(self.organizer)

    def test_validate_event_successful(self):
        """Test validate event fields successful"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': 500,
        }
        serializer = EventSerializer(data=payload)
        self.assertEqual(serializer.is_valid(), True)

    def test_validatet_too_long_title(self):
        """Test validate too long title"""
        payload = {
            'title': 'test title' * 500 ,
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': 500,
        }
        serializer = EventSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['title'])

    def test_validate_blank_title(self):
        """Test validate too long title"""
        payload = {
            'title': '',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': 500,
        }
        serializer = EventSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['title'])

    def test_validate_too_long_description(self):
        """Test validate too long description"""
        payload = {
            'title': 'test title',
            'description': 'test description'  * 500,
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': 500,
        }
        serializer = EventSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['description'])

    def test_validatet_too_long_address(self):
        """Test validate too long address"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address' * 500,
            'fee': 500,
        }
        serializer = EventSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['address'])

    def test_validate_blank_address(self):
        """Test validate blank address"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': '',
            'fee': 500,
        }
        serializer = EventSerializer(data=payload)
        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['address'])

    def test_validate_too_long_fee(self):
        """Test validate too long fee"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': 500000000000,
        }
        serializer = EventSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['fee'])

    def test_validate_full_width_fee(self):
        """Test validate full width fee"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': '５００',
        }
        serializer = EventSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), True)

    def test_validate_blank_fee(self):
        """Test validate blank fee"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
        }        
        serializer = EventSerializer(data=payload)
        self.assertEqual(serializer.is_valid(), True)
