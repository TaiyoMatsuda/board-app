import datetime

from faker import Faker

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import Participant
from core.factorys import UserFactory, EventFactory, ParticipantFactory
from event.serializers import (ListCreateParticipantSerializer,
                               UpdateParticipantSerializer)


fake = Faker()


class ParticipantSerializerApiTests(TestCase):
    """Test participant serializer API"""

    def setUp(self):
        self.organizer_user = UserFactory(email=fake.safe_email())
        self.organizer_user.first_name = fake.first_name()
        self.organizer_user.is_guide = True
        self.organizer_user.save()
        self.participant_user = UserFactory(email=fake.safe_email())
        self.participant_user.first_name = fake.first_name()
        self.participant_user.save()

        self.event = EventFactory(organizer=self.organizer_user)

        self.organizer = ParticipantFactory(
            event=self.event,
            user=self.organizer_user
        )
        self.participant = ParticipantFactory(
            event=self.event,
            user=self.participant_user
        )

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
        new_participant = UserFactory(email='new_participant@gmail.com')
        new_participant.first_name = 'newparticipant'
        new_participant.save()
        data = {
            'event': self.event.id, 'user': new_participant.id
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
        new_participant = UserFactory(email=fake.safe_email())
        new_participant.first_name = fake.first_name()
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
        new_participant = UserFactory(email=fake.safe_email())
        new_participant.first_name = fake.first_name()
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
        data = {'status': Participant.Status.CANCEL.value}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(serializer.data['status'], data['status'])

        data = {'status': Participant.Status.JOIN.value}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(serializer.data['status'], data['status'])

    def test_not_updating_participant_status_with_undesignated_number(self):
        """Test not updating participant status with undesignated number"""
        data = {'status': 2}
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['status'])

    def test_updating_wrong_field_with_UpdateParticipantSerializer(self):
        """Test not logically delting with UpdateParticipantSerializer"""
        serializer = UpdateParticipantSerializer(
            instance=self.participant, data={'is_active': False})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(self.participant.is_active)
