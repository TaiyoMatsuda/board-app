import datetime

from faker import Faker

from django.test import TestCase
from django.utils.timezone import make_aware

from core.factorys import UserFactory, EventFactory, EventCommentFactory
from event.serializers import (
    ListEventCommentSerializer, CreateEventCommentSerializer,
    UpdateEventCommentSerializer
)


fake = Faker()


class EventCommentSerializerApiTests(TestCase):
    """Test event comment serializer API"""

    def setUp(self):
        self.organaizer = UserFactory()
        self.event = EventFactory(organizer=self.organaizer)
        self.event_comment = EventCommentFactory(
            event=self.event, user=self.organaizer
        )

    def test_create_event_comment_successful(self):
        """Test create a new event comment"""
        payload = {
            'event': self.event.id,
            'user': self.organaizer.id,
            'comment': fake.text(max_nb_chars=500)
        }
        serializer = CreateEventCommentSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_event_comment_too_long_comment(self):
        """Test fail creating a new event comment because of long comment"""
        payload = {
            'event': self.event.id,
            'user': self.organaizer.id,
            'comment': 'test comment' * 100
        }
        serializer = CreateEventCommentSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['comment'])

    def test_create_event_comment_blank(self):
        """Test fail creating a new event comment because of comment blank"""
        payload = {
            'event': self.event.id,
            'user': self.organaizer.id,
            'comment': ''
        }
        serializer = CreateEventCommentSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['comment'])
