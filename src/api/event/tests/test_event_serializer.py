import datetime

from faker import Faker

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import Event
from core.factorys import UserFactory, EventFactory
from event.serializers import CreateEventSerializer


fake = Faker()


class EventSerializerApiTests(TestCase):
    """Test event serializer API"""

    def setUp(self):
        self.organizer = UserFactory(email='organizer@matsuda.com')
        self.event = EventFactory(organizer=self.organizer)

    def test_validate_event_successful(self):
        """Test validate event fields successful"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': fake.address(),
            'fee': 500,
        }
        serializer = CreateEventSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_validatet_too_long_title(self):
        """Test validate too long title"""
        payload = {
            'title': 'test title' * 500,
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': fake.address(),
            'fee': 500,
        }
        serializer = CreateEventSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['title'])

    def test_validate_blank_title(self):
        """Test validate too long title"""
        payload = {
            'title': '',
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': fake.address(),
            'fee': 500,
        }
        serializer = CreateEventSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['title'])

    def test_validate_too_long_description(self):
        """Test validate too long description"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': 'test description' * 500,
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': fake.address(),
            'fee': 500,
        }
        serializer = CreateEventSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['description'])

    def test_validatet_too_long_address(self):
        """Test validate too long address"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address' * 500,
            'fee': 500,
        }
        serializer = CreateEventSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['address'])

    def test_validate_blank_address(self):
        """Test validate blank address"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': '',
            'fee': 500,
        }
        serializer = CreateEventSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['address'])

    def test_validate_too_long_fee(self):
        """Test validate too long fee"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': fake.address(),
            'fee': 500000000000,
        }
        serializer = CreateEventSerializer(data=payload)

        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['fee'])

    def test_validate_full_width_fee(self):
        """Test validate full width fee"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
            'fee': '５００',
        }
        serializer = CreateEventSerializer(data=payload)

        self.assertTrue(serializer.is_valid())

    def test_validate_blank_fee(self):
        """Test validate blank fee"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': None,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
        }
        serializer = CreateEventSerializer(data=payload)
        self.assertTrue(serializer.is_valid())
