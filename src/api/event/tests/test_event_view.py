import datetime
import tempfile
from datetime import timedelta

from faker import Faker

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event
from core.factorys import UserFactory, EventFactory

EVENT_URL = reverse('event:event-list')


fake = Faker()


def detail_url(event_id):
    """Return event detail URL"""
    return reverse('event:event-detail', args=[event_id])


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
        self.organizer = UserFactory(email='testorganaizer@matsuda.com')
        self.first_event = EventFactory(
            organizer=self.organizer,
            event_time=make_aware(datetime.datetime.now())
        )
        self.second_event = EventFactory(
            organizer=self.organizer,
            title=fake.text(max_nb_chars=255),
            event_time=make_aware(
                datetime.datetime.now() + datetime.timedelta(days=1)),
            description=fake.text(max_nb_chars=2000),
            fee='700'
        )
        self.client = APIClient()

    def test_retrieve_event_list_success(self):
        """Test retrieving event list"""
        self.first_event.status = Event.Status.PUBLIC.value
        self.first_event.save()
        self.second_event.status = Event.Status.PUBLIC.value
        self.second_event.save()
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'start': today, 'end': tomorrow})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict_list = [
            {
                'id': self.first_event.id,
                'title': self.first_event.title,
                'image': self.first_event.image_url,
                'event_time': self.first_event.event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'address': self.first_event.address,
                'participant_count': 0
            }, {
                'id': self.second_event.id,
                'title': self.second_event.title,
                'image': self.second_event.image_url,
                'event_time': self.second_event.event_time.strftime('%Y-%m-%d %H:%M:%S'),
                'address': self.second_event.address,
                'participant_count': 0
            }
        ]
        expected_json = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": expected_json_dict_list
        }
        self.assertJSONEqual(res.content, expected_json)

    def test_retrieve_event_pagination_success(self):
        """Test retrieving event with pagination"""
        self.first_event.status = Event.Status.PUBLIC.value
        self.first_event.save()
        self.second_event.status = Event.Status.PUBLIC.value
        self.second_event.save()
        count = 0
        while count < 30:
            EventFactory(
                organizer=self.organizer,
                status=Event.Status.PUBLIC.value
            )
            count += 1

        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'start': today, 'end': tomorrow})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 30)

        res = self.client.get(
            EVENT_URL, {'start': today, 'end': tomorrow, 'page': 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_retrieving_events_for_a_day_successful(self):
        """Test retrieving events for a day"""
        self.first_event.status = Event.Status.PUBLIC.value
        self.first_event.save()
        self.second_event.status = Event.Status.PUBLIC.value
        self.second_event.save()
        EventFactory(
            organizer=self.organizer,
            event_time=make_aware(
                datetime.datetime.now() + datetime.timedelta(days=2)),
            status=Event.Status.PUBLIC.value
        )
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'start': today, 'end': tomorrow})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_not_retrieving_events_by_wrong_query_parameters_name(self):
        """Test not retrieving events by wrong query parameter name"""
        EventFactory(
            organizer=self.organizer,
            event_time=make_aware(
                datetime.datetime.now() + datetime.timedelta(days=2))
        )
        today = datetime.date.today()
        tomorrow = today + timedelta(days=1)
        res = self.client.get(EVENT_URL, {'test1': today, 'test2': tomorrow})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_retrieving_events_by_wrong_type_query_parameters(self):
        """Test not retrieving events by wrong type query parameters"""
        EventFactory(
            organizer=self.organizer,
            event_time=make_aware(
                datetime.datetime.now() + datetime.timedelta(days=2))
        )
        res = self.client.get(EVENT_URL, {'start': 'test', 'end': 'test'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_retrieving_events_by_wrong_query_parameters_number(self):
        """Test not retrieving events by wrong query parameters number"""
        EventFactory(
            organizer=self.organizer,
            event_time=make_aware(
                datetime.datetime.now() + datetime.timedelta(days=2))
        )
        today = datetime.date.today()
        res = self.client.get(EVENT_URL, {'start': today})
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
            'organizer_full_name': 'noname',
            'organizer_icon': organizer.icon_url,
            'image': event.image_url,
            'event_time': event.brief_event_time,
            'address': event.address,
            'fee': event.fee,
            'status': event.status,
            'brief_updated_at': event.brief_updated_at
        }
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_create_event_for_unauthorized_user(self):
        """Test false creating a new event"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'image': '',
            'organizer_id': self.organizer.id,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': fake.address(),
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
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': fake.address(),
            'fee': '600',
        }
        url = detail_url(self.first_event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateParticipantApiTests(TestCase):
    """Test the authorized user event API"""

    def setUp(self):
        self.client = APIClient()
        self.organizer = UserFactory(email='testorganizer@matsuda.com')
        self.organizer.is_guide = True
        self.organizer.save()
        self.user_one = UserFactory(email='testone@matsuda.com')

        self.event = EventFactory(organizer=self.organizer)

        self.client.force_authenticate(self.organizer)

    def test_create_event_successful(self):
        """Test create a new event"""
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'organizer': self.organizer.id,
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': fake.address(),
            'fee': 500,
            'status': '1'
        }
        res = self.client.post(EVENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_not_creating_event_by_tourist(self):
        """Test not creating a new event by tourist"""
        self.client.force_authenticate(self.user_one)
        payload = {
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': fake.address(),
            'fee': 500,
            'status': '1'
        }
        res = self.client.post(EVENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_logically_delete_event_false(self):
        """Test logically disable to delete an event for unsuitable user"""
        url = detail_url(self.event.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(self.event.is_active)

    def test_logically_delete_event_successful(self):
        """Test logically delete an event for authenticated user"""
        self.organizer.is_staff = True
        self.organizer.save()
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
                'title': fake.text(max_nb_chars=255),
                'description': fake.text(max_nb_chars=2000),
                'image': ntf,
                'event_time': make_aware(datetime.datetime.now()),
                'address': fake.address(),
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
            'title': fake.text(max_nb_chars=255),
            'description': fake.text(max_nb_chars=2000),
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': fake.address(),
            'fee': '600',
            'status': '2'
        }
        url = detail_url(self.event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
