import datetime

from unittest.mock import patch

from faker import Faker

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import make_aware

from core import models
from core.factorys import UserFactory, EventFactory


fake = Faker()


class ModelTests(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.event = EventFactory(organizer=self.user)

    def test_create_user_with_email_successful(self):
        """Test creating a new user withh an email is successful"""
        email = fake.safe_email()
        password = 'Testpass123'
        user = get_user_model().objects.create_user(email, password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test2@MATSUDA.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""

        email = fake.safe_email()
        password = 'Testpass123'
        user = get_user_model().objects.create_superuser(email, password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    @patch('uuid.uuid4')
    def test_icon_file_name_uuid(self, mock_uuid):
        """Test that icon image is saved in the correct location"""
        uuid = fake.text(max_nb_chars=20)
        mock_uuid.return_value = uuid
        file_path = models.user_icon_file_path(None, 'iconimage.jpg')

        exp_path = f'uploads/user/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    def test_event_str(self):
        """Test the event string representations"""
        create_event = models.Event.objects.create(
            title=fake.text(max_nb_chars=255),
            description=fake.text(max_nb_chars=2000),
            organizer=self.user,
            event_time=make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            address=fake.address(),
            fee=50
        )

        self.assertEqual(str(create_event), create_event.title)

    @patch('uuid.uuid4')
    def test_event_file_name_uuid(self, mock_uuid):
        """Test that event image is saved in the correct location"""
        uuid = fake.text(max_nb_chars=20)
        mock_uuid.return_value = uuid
        file_path = models.event_image_file_path(None, 'eventimage.jpg')

        exp_path = f'uploads/event/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    def test_event_comment_str(self):
        """Test the event_comment string representations"""
        email = fake.safe_email()
        password = 'Testpass123'
        comment_user = get_user_model().objects.create_user(email, password)

        event_comment = models.EventComment.objects.create(
            event=self.event,
            user=comment_user,
            comment=fake.text(max_nb_chars=500),
        )

        self.assertEqual(str(event_comment), event_comment.comment)

    def test_participant_str(self):
        """Test the participant string representations"""
        email = fake.safe_email()
        password = 'Testpass123'
        user = get_user_model().objects.create_user(email, password)

        participant = models.Participant.objects.create(
            event=self.event,
            user=user,
        )
        self.assertEqual(str(participant), participant.user.short_name)
