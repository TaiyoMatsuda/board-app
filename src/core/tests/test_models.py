from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
import datetime
from core import models


def sample_user(email='test@matsuda.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_event():
    """Create a sample event"""
    return models.Event.objects.create(
        title='sample event',
        organizer=sample_user(),
        event_time=make_aware(datetime.datetime.now())
        .strftime('%Y-%m-%d %H:%M:%S'),
        address='sample test place'
    )


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a neww user withh an email is successful"""
        email = 'test@matsuda.com'
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

        email = 'test3@matsuda.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_superuser(email, password)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    @patch('uuid.uuid4')
    def test_icon_file_name_uuid(self, mock_uuid):
        """Test that icon image is saved in the correct location"""
        uuid = 'icon-test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.user_icon_file_path(None, 'icontimage.jpg')

        exp_path = f'uploads/user/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    def test_event_str(self):
        """Test the event string representations"""
        event = models.Event.objects.create(
            title='test event',
            organizer=sample_user(),
            event_time=make_aware(datetime.datetime.now())
            .strftime('%Y-%m-%d %H:%M:%S'),
            address='testplace'
        )

        self.assertEqual(str(event), event.title)

    @patch('uuid.uuid4')
    def test_event_file_name_uuid(self, mock_uuid):
        """Test that event image is saved in the correct location"""
        uuid = 'event-test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.event_image_file_path(None, 'eventimage.jpg')

        exp_path = f'uploads/event/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    def test_event_comment_str(self):
        """Test the event_comment string representations"""
        email = 'comment_user@matsuda.com'
        password = 'Testpass123'
        comment_user = get_user_model().objects.create_user(email, password)

        event_comment = models.EventComment.objects.create(
            event=sample_event(),
            user=comment_user,
            comment='test comment',
        )

        self.assertEqual(str(event_comment), event_comment.comment)

    def test_candidate_str(self):
        """Test the candidate string representations"""
        email = 'candidate@matsuda.com'
        password = 'Testpass123'
        candidate = get_user_model().objects.create_user(email, password)

        candidate = models.EventComment.objects.create(
            event=sample_event(),
            user=candidate,
        )

        self.assertEqual(str(candidate), candidate.user.get_full_name())
