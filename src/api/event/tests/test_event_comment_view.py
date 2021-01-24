from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils.timezone import make_aware, localtime
import datetime

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event, EventComment


def detail_url(event_id):
    """Return detail event comment URL"""
    return reverse('event:eventComment', args=[event_id])


def delete_url(event_id, comment_id):
    """Return delete event comment URL"""
    return reverse('event:deleteComment', args=[event_id, comment_id])


def sample_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)


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
        'status': '1',
    }

    return Event.objects.create(organizer=user, **default)


def sample_event_comment(event, user, comment='test comment'):
    """Create and return a sample event comment"""
    default = {'event': event, 'user': user, 'comment': comment}
    return EventComment.objects.create(**default)


def get_event_comment_by_json(**params):

    event_comment = EventComment.objects.get(id=params['id'])
    expected_json_dict = {
        'id': event_comment.id,
        'user': {
            'first_name': event_comment.user.first_name,
            'is_active': event_comment.user.is_active,
            'icon': None
        },
        'comment': event_comment.comment,
        'brief_updated_at': localtime(event_comment.updated_at)
        .strftime('%Y-%m-%d %H:%M:%S')
    }
    return expected_json_dict


class PublicEventCommentApiTests(TestCase):
    """Test that publcly available event comments API"""

    def setUp(self):
        self.user = sample_user(
            email='test@matsuda.com',
            password='testpass',
            first_name='test'
        )
        self.event = sample_event(self.user)
        self.event_comment = sample_event_comment(self.event, self.user)
        self.deleted_comment = sample_event_comment(self.event, self.user)
        self.deleted_comment.delete()
        self.deleted_comment.refresh_from_db()
        self.client = APIClient()

    def test_retrieve_event_comment_success(self):
        """Test retrieving event comments"""
        url = detail_url(self.event.id)
        res = self.client.get(url, {'page': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        event_comments = EventComment.objects.filter(
            is_active=True).order_by('updated_at')
        expected_json_dict_list = []
        for event_comment in event_comments:
            expected_json_dict = {
                'id': event_comment.id,
                'event': event_comment.event.id,
                'user': event_comment.user.id,
                'first_name': event_comment.user.first_name,
                'icon': event_comment.user.get_icon_url,
                'comment': event_comment.comment,
                'brief_updated_at': event_comment.get_brief_updated_at
            }
            expected_json_dict_list.append(expected_json_dict)

        expected_json = {
            "count": len(event_comments),
            "next": None,
            "previous": None,
            "results": expected_json_dict_list
        }
        self.assertJSONEqual(res.content, expected_json)

    def test_retrieve_event_comment_pagination_success(self):
        """Test retrieving event comments with pagination"""
        count = 0
        while count < 15:
            sample_event_comment(self.event, self.user)
            count += 1

        url = detail_url(self.event.id)
        res = self.client.get(url, {'page': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 15)

        res = self.client.get(url, {'page': 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_retrieve_event_comment_pagination_false(self):
        """Test retrieving event comments false with pagination"""
        url = detail_url(self.event.id)
        res = self.client.get(url, {'page': 0})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        res = self.client.get(url, {'page': 2})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_retrieve_deleted_comments(self):
        """Test not retrieving deleted comments"""
        url = detail_url(self.event.id)
        res = self.client.get(url, {'page': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict = {
            'id': self.event_comment.id,
            'event': self.event_comment.event.id,
            'user': self.event_comment.user.id,
            'first_name': self.event_comment.user.first_name,
            'icon': self.event_comment.user.get_icon_url,
            'comment': self.event_comment.comment,
            'brief_updated_at': self.event_comment.get_brief_updated_at
        }
        self.assertIn(expected_json_dict, list(res.data['results']))
        self.assertEqual(dict(res.data['results'][0]), expected_json_dict)

    def test_create_event_comment_for_unauthorized_user(self):
        """Test creating a new event comment"""
        payload = {
            'comment': 'testcomment',
        }
        url = detail_url(self.event.id)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event_comment_for_unauthorized_user(self):
        """Test delete an event comment for authenticated user"""
        url = delete_url(self.event.id, self.event_comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEventCommentApiTests(TestCase):
    """Test the authorized user Event comment API"""

    def setUp(self):
        self.client = APIClient()
        self.organizer = sample_user(
            email='test@matsuda.com',
            password='testpass',
            first_name='test'
        )
        self.comment_user = sample_user(
            email='test2@matsuda.com',
            password='testpass2',
            first_name='testtest'
        )
        self.event = sample_event(self.organizer)
        self.private_event = sample_event(self.organizer)
        self.private_event.status = '0'
        self.private_event.save()
        self.organizer_comment = sample_event_comment(
            self.event, self.organizer)
        self.event_comment = sample_event_comment(
            self.event, self.comment_user)
        self.client.force_authenticate(self.organizer)

    def test_create_event_comment_successful(self):
        """Test creating a new event comment"""
        str_comment = 'test_create_event_comment_successful'
        payload = {
            'comment': str_comment,
        }
        url = detail_url(self.event.id)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        new_event_comment = EventComment.objects.latest('updated_at')
        self.assertEqual(new_event_comment.comment, str_comment)

    def test_not_create_event_comment_to_private_event(self):
        """Test not creating a new comment to private event"""
        payload = {
            'comment': 'testcomment',
        }
        url = detail_url(self.private_event.id)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_create_event_comment_to_deleted_event(self):
        """Test not creating a new comment to deleted event"""
        self.event.delete()

        payload = {
            'comment': 'testcomment',
        }
        url = detail_url(self.event.id)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_comment(self):
        """Test delete the event comment by authenticated user"""
        url = delete_url(self.event.id, self.organizer_comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.organizer_comment.refresh_from_db()

        self.assertFalse(self.organizer_comment.is_active)

    def test_not_delete_event_comment_for_anyone(self):
        """Test not delete an event comment by not suitable user"""
        url = delete_url(self.event.id, self.event_comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
