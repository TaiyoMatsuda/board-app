from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import make_aware
import datetime

from core.models import Event, Participant

from event.serializers import (
    ListCreateParticipantSerializer, UpdateParticipantSerializer
)


def sample_user(**params):
    """Create and return a sample user"""
    return get_user_model().objects.create_user(**params)


def sample_event(user):
    """Create and return a sample comment"""
    default = {
        'title': 'test title',
        'description': 'test description',
        'organizer': user,
        'image': None,
        'event_time': make_aware(datetime.datetime.now())
        .strftime('%Y-%m-%d %H:%M:%S'),
        'address': 'test address',
        'fee': 500,
    }

    return Event.objects.create(**default)


def sample_participant(event, user, **params):
    """Create and return a sample participant"""
    return Participant.objects.create(event=event, user=user, **params)


class ParticipantSerializerApiTests(TestCase):
    """Test participant serializer API"""

    def setUp(self):
        self.organizer_user = sample_user(
            email='organizer@gmail.com',
            password='testpass'
        )
        self.organizer_user.first_name = 'organizer'
        self.organizer_user.is_guide = True
        self.organizer_user.save()
        self.participant_user = sample_user(
            email='participant@gmail.com',
            password='testpass'
        )
        self.participant_user.first_name = 'participant'
        self.participant_user.save()

        self.event = sample_event(self.organizer_user)

        self.organizer = sample_participant(self.event, self.organizer_user)
        self.participant = sample_participant(
            self.event, self.participant_user)

    def test_retrieve_participant_successful(self):
        """Test retrieving participant successful"""
        participants = Participant.objects.filter(event=self.event)
        serializer = ListCreateParticipantSerializer(
            instance=participants, many=True)

        expected_dict_list = [
            {
                'user': self.organizer_user.id,
                'first_name': self.organizer_user.first_name,
                'icon': '/static/images/no_user_image.png'
            },
            {
                'user': self.participant_user.id,
                'first_name': self.participant_user.first_name,
                'icon': '/static/images/no_user_image.png'
            }
        ]
        self.assertEqual(serializer.data, expected_dict_list)

    def test_creating_participant_successful(self):
        """Test creating participant successful"""
        new_participant = sample_user(
            email='new_participant@gmail.com',
            password='testpass'
        )
        new_participant.first_name = 'newparticipant'
        new_participant.save()
        data = {
            'event': self.event.id,
            'user': new_participant.id
        }
        serializer = ListCreateParticipantSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        expected_dict = {
            'user': new_participant.id,
            'first_name': new_participant.first_name,
            'icon': '/static/images/no_user_image.png'
        }
        self.assertEqual(serializer.data, expected_dict)

    def test_not_creating_participant_with_wrong_event_id_type(self):
        """Test not creating participant with worng event id type"""
        new_participant = sample_user(
            email='new_participant@gmail.com',
            password='testpass'
        )
        new_participant.first_name = 'newparticipant'
        new_participant.save()
        data = {
            'event': self.event,
            'user': new_participant.id
        }
        serializer = ListCreateParticipantSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['event'])

    def test_not_creating_participant_with_wrong_user_id_type(self):
        """Test not creating participant with worng user id type"""
        new_participant = sample_user(
            email='new_participant@gmail.com',
            password='testpass'
        )
        new_participant.first_name = 'newparticipant'
        new_participant.save()
        data = {
            'event': self.event.id,
            'user': new_participant
        }
        serializer = ListCreateParticipantSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['user'])

    def test_update_participant_status_successful(self):
        """Test updating participant status successful"""
        data = {'status': 0}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(int(serializer.data['status']), data['status'])

        data = {'status': 1}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(int(serializer.data['status']), data['status'])

    def test_not_updating_participant_status_with_undesignated_number(self):
        """Test not updating participant status with undesignated number"""
        data = {'status': 2}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['status'])

    def test_not_updating_participant_status_with_other_type(self):
        """Test not updating participant status with undesignated number"""
        data = {'status': '2'}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['status'])

    def test_updating_wrong_field_with_UpdateParticipantSerializer(self):
        """Test not logically delting with UpdateParticipantSerializer"""
        data = {'is_active': False}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(self.participant.is_active)
