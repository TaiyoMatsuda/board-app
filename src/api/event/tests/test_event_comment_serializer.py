import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import Event, EventComment
from core.factorys import UserFactory
from event.serializers import ListCreateEventCommentSerializer


def sample_event(user):
    """Create and return a sample event"""
    default = {
        'title': 'test title',
        'description': 'test description',
        'image': None,
        'event_time': make_aware(datetime.datetime.now())
        .strftime('%Y-%m-%d %H:%M:%S'),
        'address': 'test address',
        'fee': 500,
    }

    return Event.objects.create(organizer=user, **default)


def sample_event_comment(event, user, comment='test comment', **params):
    """Create and return a sample comment"""
    default = {
        'event': event,
        'user': user,
        'comment': comment,
    }
    default.update(params)

    return EventComment.objects.create(**default)


class EventCommentSerializerApiTests(TestCase):
    """Test event comment serializer API"""

    def setUp(self):
        self.organaizer = UserFactory(email='organaizer@matsuda.com')
        self.event = sample_event(self.organaizer)
        self.event_comment = sample_event_comment(
            self.event,
            self.organaizer
        )

    def test_create_event_comment_successful(self):
        """Test create a new event comment"""
        payload = {
            'event': self.event.id,
            'user': self.organaizer.id,
            'comment': 'test comment'
        }
        serializer = ListCreateEventCommentSerializer(data=payload)
        self.assertTrue(serializer.is_valid())

    def test_event_comment_too_long_comment(self):
        """Test fail creating a new event comment because of long comment"""
        payload = {
            'event': self.event.id,
            'user': self.organaizer.id,
            'comment': 'test comment' * 100
        }
        serializer = ListCreateEventCommentSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['comment'])

    def test_create_event_comment_blank(self):
        """Test fail creating a new event comment because of comment blank"""
        payload = {
            'event': self.event.id,
            'user': self.organaizer.id,
            'comment': ''
        }
        serializer = ListCreateEventCommentSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['comment'])
