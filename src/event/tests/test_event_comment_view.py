from django.contrib.auth imoprt get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework import APIClient

from core.models import EventComment

from event.serializers import EventCommentSerializer

EVENT_COMMENT_URL = reverse('event:event-comment')
CREATE_EVENT_COMMENT_URL = reverse('event:create-event-comment')

def detail_url(event_comment_id):
    """Return event comment detail URL"""
    return reverse('event:update-comment-detail', args=[event_comment_id])

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

def get_event_comment_by_json(**params):
    event_comment = EventComment.objects.get(
        event=params['event'],
        user=params['user'],
        update_at=params['update_at'],
    )

    expected_json_dict = {
        '1':
            'event': event_comment.event,
            'user': event_comment.user,
            'comment': useevent_commentr.comment,
            'update_at': event_comment.update_at,
            'is_active': event_comment.is_active
    }

    return expected_json_dict

class PublicEventCommentApiTests(TestCase):
    """Test that publcly available event comments API"""

    def setUp(self):
        self.user = sample_user(email='test@matsuda.com', password='testpass')
        self.event = sample_event([self.user.id])
        sample_event_comment([self.event.id], [self.user.id])
        sample_event_comment([self.event.id], [self.user.id])

        self.client = APIClient()

    def test_retrieve_event_comment_success(self):
        """Test retrieving event comments"""

        res = self.client.get(EVENT_COMMENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        event_comment = EventComment.all().order_by('-update_at')
        expected_json_dict = {
            '1':
                'event': event_comment.event,
                'user': event_comment.user,
                'comment': event_comment.comment,
                'update_at': event_comment.update_at,
                'is_active': event_comment.is_active,
            '2':
                'event': event_comment.event,
                'user': event_comment.user,
                'comment': event_comment.comment,
                'update_at': event_comment.update_at,
                'is_active': event_comment.is_active,
        }

        self.assertJSONEqual(res.content, expected_json_dict)

    def test_create_event_comment_for_unauthorized_user(self):
        """Test creating a new event comment"""
        payload = {
            'event': [self.event.id],
            'user': [self.user.id],
            'comment': 'testcomment',
        }
        res = self.client.post(CREATE_EVENT_COMMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_event_comment_for_unauthorized_user(self):
        """Test partial updating the event comment for authenticated user"""
        payload = {
            'is_active': False
        }
        url = detail_url(self.event_comment.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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
            'comment': 'testcomment',
        }
        res = self.client.post(CREATE_EVENT_COMMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        expected_json_dict = get_event_comment_by_json(**res.data)

        self.assertJSONEqual(res.content, expected_json_dict)

    def test_partial_update_event_comment(self):
        """Test partial updating the event comment for authenticated user"""
        payload = {
            'is_active': False
        }
        url = detail_url(self.event_comment.id)
        res = self.client.patch(url, payload)

        self.event_comment.refesh_from_db()

        expected_json_dict = get_event_comment_by_json(**res.data)

        self.assertJSONEqual(res.content, expected_json_dict)
