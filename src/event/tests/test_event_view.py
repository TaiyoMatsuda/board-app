import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import timedelta

import datetime

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event

from event.serializers import EventSerializer

EVENT_URL = reverse('event:event-list')

def detail_url(event_id):
    """Return event detail URL"""
    return reverse('event:event-detail', args=[event_id])

def sample_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)

def sample_event(
    organizer,
    title='test title',
    description='test description',
    event_time=make_aware(datetime.datetime.now()),
    address='test address',
    fee=500
    ):

    """Create and return a sample event"""
    default = {
        'title': title,
        'description': description,
        'organizer': organizer,
        'image': '',
        'event_time': event_time.strftime('%Y-%m-%d %H:%M:%S'),
        'address': address,
        'fee': fee,
    }
    return Event.objects.create(**default)

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
        self.organizer = sample_user(
            email='testorganaizer@matsuda.com',
            password='testpass'
        )
        self.first_event = sample_event(organizer=self.organizer)
        self.second_event = sample_event(
            organizer=self.organizer,
            title='second event title',
            event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=1)),
            description='second event description',
            address='second event address',
            fee='700'
        )
        self.client = APIClient()


    def test_retrieve_event_list_success(self):
        """Test retrieving event list"""
        res = self.client.get(EVENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        event = Event.objects.all().order_by('-event_time')
        expected_json_dict = [
            {
                'id': self.first_event.id,
                'title': self.first_event.title,
                'image': self.first_event.get_image_url,
                'event_time': self.first_event.event_time,
                'address': self.first_event.address,
                'participant_count': 0
            },{
                'id': self.second_event.id,
                'title': self.second_event.title,
                'image': self.second_event.get_image_url,
                'event_time': self.second_event.event_time,
                'address': self.second_event.address,
                'participant_count': 0
            }
        ]
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_retrieve_maximum_ten_events_success(self):
        """Test retrieving mzximum ten events"""
        count= 0
        while count < 10:
            sample_event(organizer=self.organizer)
            count += 1

        res = self.client.get(EVENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 10)

    # def test_retrieving_events_for_a_day_successful(self):
    #     """Test retrieving events for a day"""
    #     sample_event(
    #         organizer=self.organizer,
    #         event_time=make_aware(datetime.datetime.now() + datetime.timedelta(days=2))
    #     )
    #     today = datetime.date.today()
    #     tomorrow = today + timedelta(days=1)
    #     breakpoint()
    #     res = self.client.get(EVENT_URL, {'event_time__gt':today, 'event_time__lt':tomorrow})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 2)

    # def test_retrieve_event_success(self):
    #     """Test retrieving event"""
    #     url = detail_url(self.second_event.id)
    #     breakpoint()
    #     res = self.client.get(url)
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #
    #     event = Event.object.get(event_id=[self.first_event.id])
    #
    #     eventt_list = []
    #     for event in eventt_list:
    #         event_dict = {
    #             'event_id': event.id,
    #             'title': event.title,
    #             'description': event.description,
    #             'organizer_id': event.organizer_id,
    #             'organizer_first_name': event.organizer_first_name,
    #             'organizer_icon': event.organizer_icon,
    #             'image': event.image,
    #             'event_time': event.event_time,
    #             'address': event.address,
    #             'fee': event.fee,
    #             # 'event_comment_list': {
    #             #     'event_comment_id': event.event_comment.id
    #             #     'user': event.event_comment.user,
    #             #     'first_name': event_comment.user.first_name,
    #             #     'icon': None,
    #             #     'comment': event_comment.user.comment,
    #             #     'brief_updated_at': localtime(event_comment.updated_at).strftime('%Y-%m-%d %H:%M:%S')
    #             # },
    #             # 'participant_list': {
    #             #     'user_id': event.participant.user_id,
    #             #     'first_name': event.participant.first_name,
    #             #     'icon': None
    #             # },
    #             'participant_count': event.participant_count,
    #             'brief_updated_at': localtime(event_comment.updated_at).strftime('%Y-%m-%d %H:%M:%S')
    #         }
    #         event_comment_list.append(event_comment_dict)
    #
    #     # participant_list = []
    #     # for participant in participant_list:
    #     #     participant_dict = {
    #     #         'user': {
    #     #             '': participant.user,
    #     #             '':
    #     #         },
    #     #         'is_active': participant.is_active,
    #     #         'updated_at': participant.updated_at,
    #     #     }
    #     #     participant_list.appent(participant_dict)
    #     expected_json_dict = [
    #         {
    #             'id': event.id,
    #             'title': event.title,
    #             'description': event.description,
    #             'organizer': {
    #                 'first_name': event.user.first_name,
    #                 'is_active': event.user.is_active,
    #                 'icon': ''
    #             },
    #             'event_time': str(localtime(event_comment.updated_at)).replace(' ', 'T'),
    #             'address': event.address,
    #             'fee': event.fee,
    #             'event_comment': event_comment_list,
    #             'participant': participant_list
    #         }
    #     ]
    #
    #     self.assertJSONEqual(res.content, expected_json_dict)

    def test_create_event_for_unauthorized_user(self):
        """Test false creating a new event"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'organizer_id': self.organizer.id,
            'event_time': make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            'address': 'test address',
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
            'title': 'test update title',
            'description': 'test update description',
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test update address',
            'fee': '600',
        }
        url = detail_url(self.first_event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateParticipantApiTests(TestCase):
    """Test the authorized user event API"""

    def setUp(self):
        self.client = APIClient()
        self.organizer = sample_user(
            email='testorganizer@matsuda.com',
            password='testpass'
        )
        self.organizer.is_guide = True
        self.organizer.save()
        self.user_one = sample_user(
            email='testone@matsuda.com',
            password='testpass'
        )

        self.event = sample_event(self.organizer)

        self.client.force_authenticate(self.organizer)

    def test_create_event_successful(self):
        """Test create a new event"""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test address',
            'fee': 500,
            'status': '1'
        }
        res = self.client.post(EVENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_logically_delete_event(self):
        """Test logically delete an event for authenticated user"""
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
                'title': 'test update title',
                'description': 'test update description',
                'image': ntf,
                'event_time': make_aware(datetime.datetime.now()),
                'address': 'test update address',
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
            'title': 'test update title',
            'description': 'test update description',
            'image': '',
            'event_time': make_aware(datetime.datetime.now()),
            'address': 'test update address',
            'fee': '600',
            'status': '2'
        }
        url = detail_url(self.event.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
