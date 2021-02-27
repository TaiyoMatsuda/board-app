import datetime

from faker import Faker

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime, make_aware
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event, EventComment
from core.factorys import UserFactory, EventFactory, EventCommentFactory


fake = Faker()


def detail_url(event_id):
    """Return detail event comment URL"""
    return reverse('event:eventComment', args=[event_id])


def status_url(event_id, comment_id):
    """Return status event comment URL"""
    return reverse('event:statusComment', args=[event_id, comment_id])


def delete_url(event_id, comment_id):
    """Return delete event comment URL"""
    return reverse('event:deleteComment', args=[event_id, comment_id])


def get_event_comment_by_json(**params):

    event_comment = EventComment.objects.get(id=params['id'])
    expected_json_dict = {
        'id': event_comment.id,
        'user': {
            'first_name': event_comment.user.first_name,
            'is_active': event_comment.user.is_active,
            'icon': None
        },
        'comment': event_comment.display_comment,
        'brief_updated_at': localtime(event_comment.updated_at)
        .strftime('%Y-%m-%d %H:%M:%S')
    }
    return expected_json_dict


class PublicEventCommentApiTests(TestCase):
    """Test that publcly available event comments API"""

    def setUp(self):
        self.user = UserFactory(first_name=fake.first_name())
        self.event = EventFactory(organizer=self.user)
        self.event_comment = EventCommentFactory(
            event=self.event, user=self.user
        )
        self.deleted_comment = EventCommentFactory(
            event=self.event, user=self.user
        )
        self.deleted_comment.delete()
        self.deleted_comment.refresh_from_db()
        self.client = APIClient()

    def test_retrieve_event_comment_success(self):
        """Test retrieving event comments"""
        url = detail_url(self.event.id)
        res = self.client.get(url, {'page': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        event_comments = EventComment.objects.all().order_by('updated_at')
        expected_json_dict_list = []
        for event_comment in event_comments:
            expected_json_dict = {
                'id': event_comment.id,
                'event': event_comment.event.id,
                'user': event_comment.user.id,
                'first_name': event_comment.user.first_name,
                'icon': event_comment.user.icon_url,
                'comment': event_comment.display_comment,
                'status': event_comment.status,
                'brief_updated_at': event_comment.brief_updated_at
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
            EventCommentFactory(
                event=self.event, user=self.user
            )
            count += 1

        url = detail_url(self.event.id)
        res = self.client.get(url, {'page': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 15)

        res = self.client.get(url, {'page': 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

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
            'icon': self.event_comment.user.icon_url,
            'comment': self.event_comment.display_comment,
            'status': self.event_comment.status,
            'brief_updated_at': self.event_comment.brief_updated_at
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
        self.organizer = UserFactory(
            email=fake.safe_email(),
            first_name=fake.first_name()
        )
        self.comment_user = UserFactory(
            email=fake.safe_email(),
            first_name=fake.first_name()
        )
        self.event = EventFactory(organizer=self.organizer)
        self.private_event = EventFactory(organizer=self.organizer)
        self.private_event.status = Event.Status.PRIVATE.value
        self.private_event.save()
        self.organizer_comment = EventCommentFactory(
            event=self.event, user=self.organizer
        )
        self.event_comment = EventCommentFactory(
            event=self.event, user=self.comment_user
        )
        self.client.force_authenticate(self.organizer)

    def test_create_event_comment_successful(self):
        """Test creating a new event comment"""
        str_comment = fake.text(max_nb_chars=500)
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
            'comment': fake.text(max_nb_chars=500),
        }
        url = detail_url(self.private_event.id)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_event_comment_status(self):
        """Test change event comment status"""
        self.client.force_authenticate(self.comment_user)
        url = status_url(self.event.id, self.event_comment.id)
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.event_comment.refresh_from_db()

        self.assertEqual(self.event_comment.status,
                        EventComment.Status.EDITED.value)

    def test_not_create_event_comment_to_deleted_event(self):
        """Test not creating a new comment to deleted event"""
        self.event.delete()

        payload = {'comment': fake.text(max_nb_chars=500),}
        url = detail_url(self.event.id)
        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_event_comment_false(self):
        """Test delete the event comment by unsuitable user"""
        url = delete_url(self.event.id, self.organizer_comment.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.event.is_active)

    def test_delete_event_comment_successful(self):
        """Test delete the event comment by authenticated user"""
        self.organizer.is_staff = True
        self.organizer.save()
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
