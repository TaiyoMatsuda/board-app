from django.contrib.auth imoprt get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework import APIClient

from core.models import EventComment

from event.serializers import EventCommentSerializer

CREATE_EVENT_COMMENT_URL = reverse('event:create-event-comment')

def sample_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)

def sample_event(user, **params):
    """Create and return a sample comment"""
    default = {
        'title': 'test title',
        'description': 'test description',
        'image': None,
        'event_time': timezone.now,
        'address': 'test address',
        'fee': '500'
    }
    defaults.update(params)

    return EventComment.object.create(event=event, organizer=user,
     comment=comment, **default)

def sample_event_comment(event, user, comment='test comment', **params):
    """Create and return a sample comment"""
    return EventComment.object.create(event=event, user=user, comment=comment,
    **params)


class PrivateEventCommentApiTests(TestCase):
    """Test the authorized user Event comment API"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(email='test@matsuda.com', password='testpass')
        self.event = sample_event([self.user.id])
        self.event_comment = sample_event_comment(
            [self.event.id],
            [self.user.id]
        )
        self.client.force_authenticate(self.user)

    def test_create_event_comment_successful(self):
        """Test creating a new event comment"""
        payload = {
            'event': [self.event.id],
            'user': [self.user.id],
            'comment': 'test comment' * 100
        }
        res = self.client.post(CREATE_EVENT_COMMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        expected_json_dict = get_event_comment_by_json(**res.data)

        self.assertJSONEqual(res.content, expected_json_dict)
