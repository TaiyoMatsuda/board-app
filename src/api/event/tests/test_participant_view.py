from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils.timezone import make_aware
import datetime

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event, Participant


def listCreate_url(event_id):
    """Return create detail URL"""
    return reverse('event:listCreateParticipant', args=[event_id])


def cancel_url(event_id):
    """Return update status URL"""
    return reverse('event:cancelParticipant', args=[event_id])


def join_url(event_id):
    """Return update status URL"""
    return reverse('event:joinParticipant', args=[event_id])


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


def sample_participant(event, user, **params):
    """Create and return a sample participant"""
    return Participant.objects.create(event=event, user=user, **params)


class PublicParticipantApiTests(TestCase):
    """Test that publcly available participant API"""

    def setUp(self):
        self.organizer = sample_user(
            email='organizer@matsuda.com',
            password='testpass',
            first_name='organizer'
        )
        self.new_organizer = sample_user(
            email='new_organizer@matsuda.com',
            password='testpass',
            first_name='neworganizer'
        )
        self.follower = sample_user(
            email='follower@matsuda.com',
            password='testpass',
            first_name='follower'
        )

        self.event = sample_event(self.organizer)
        self.event_two = sample_event(self.organizer)
        self.participant_one = sample_participant(
            self.event,
            self.organizer
        )
        self.participant_two = sample_participant(
            self.event,
            self.follower
        )
        self.participant_three = sample_participant(
            self.event_two,
            self.organizer
        )

        self.client = APIClient()

    def test_retrieve_participants_success(self):
        """Test retrieving participants"""
        url = listCreate_url(self.event.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        participants = Participant.objects.filter(
            event=self.event.id).order_by('updated_at')
        expected_json_dict_list = []
        for participant in participants:
            expected_json_dict = {
                'user': participant.user.id,
                'first_name': participant.user.first_name,
                'icon': participant.user.icon_url
            }
            expected_json_dict_list.append(expected_json_dict)

        self.assertJSONEqual(res.content, expected_json_dict_list)

    def test_not_retrieve_deleted_participants_success(self):
        """Test not retrieving deleted participants"""
        self.participant_two.delete()

        url = listCreate_url(self.event.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict_list = [{
            'user': self.participant_one.user.id,
            'first_name': self.participant_one.user.first_name,
            'icon': self.participant_one.user.icon_url
        }]
        self.assertJSONEqual(res.content, expected_json_dict_list)

    def test_not_retrieve_cancel_participants_success(self):
        """Test not retrieving canceled participants"""
        self.participant_two.status = '0'
        self.participant_two.save()

        url = listCreate_url(self.event.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict_list = [{
            'user': self.participant_one.user.id,
            'first_name': self.participant_one.user.first_name,
            'icon': self.participant_one.user.icon_url
        }]
        self.assertJSONEqual(res.content, expected_json_dict_list)

    def test_create_participant_for_unauthorized_user(self):
        """Test creating a new participant for unauthorized user"""
        url = listCreate_url(self.event.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_participant_for_unauthorized_user(self):
        """Test canceling a new participant for unauthorized user"""
        url = cancel_url(self.event.id)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_join_participant_for_unauthorized_user(self):
        """Test joinning a new participant for unauthorized user"""
        url = join_url(self.event.id)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateParticipantApiTests(TestCase):
    """Test the authorized user participant API"""

    def setUp(self):
        self.client = APIClient()
        self.organizer = sample_user(
            email='organizer@matsuda.com',
            password='testpass',
            first_name='organizer'
        )
        self.new_organizer = sample_user(
            email='new_organizer@matsuda.com',
            password='testpass',
            first_name='new_organizer'
        )
        self.follower = sample_user(
            email='follower@matsuda.com',
            password='testpass',
            first_name='follower'
        )
        self.event = sample_event(self.organizer)
        self.private_event = sample_event(self.organizer)
        self.private_event.status = '0'
        self.private_event.save()
        self.cancel_event = sample_event(self.organizer)
        self.cancel_event.status = '2'
        self.cancel_event.save()
        self.participant = sample_participant(
            self.event,
            self.follower
        )

    def test_create_participant_successful(self):
        """Test creating a new participant"""
        self.client.force_authenticate(self.new_organizer)

        url = listCreate_url(self.event.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_not_create_the_same_participant(self):
        """Test not creating the same participant"""
        self.client.force_authenticate(self.new_organizer)

        url = listCreate_url(self.event.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_create_participant_in_private_event(self):
        """Test not creating a new participant in private event"""
        self.client.force_authenticate(self.new_organizer)

        url = listCreate_url(self.private_event.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_create_participant_in_canceled_event(self):
        """Test not creating a new participant in canceled event"""
        self.client.force_authenticate(self.new_organizer)

        url = listCreate_url(self.cancel_event.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_create_participant_in_deleted_event(self):
        """Test not creating a new participant in deleted event"""
        self.client.force_authenticate(self.new_organizer)

        self.event.delete()

        url = listCreate_url(self.event.id)
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_participant(self):
        """Test canceling a participant"""
        self.client.force_authenticate(self.follower)
        url = cancel_url(self.event.id)
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.participant.refresh_from_db()

        self.assertEqual(self.participant.status, '0')

    def test_join_participant(self):
        """Test joinning a participant"""
        self.client.force_authenticate(self.follower)

        self.participant.status = '0'
        self.participant.save()
        self.participant.refresh_from_db()

        url = join_url(self.event.id)
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.participant.refresh_from_db()

        self.assertEqual(self.participant.status, '1')
