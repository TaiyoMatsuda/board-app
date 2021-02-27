import datetime
import os
import tempfile

from faker import Faker

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Event, Participant, EventComment
from core.factorys import (
    UserFactory, EventFactory, ParticipantFactory, EventCommentFactory
)

USER_URL = reverse('user:user-list')


fake = Faker()


def detail_url(user_id):
    """Return user detail URL"""
    return reverse('user:user-detail', args=[user_id])


def show_user_url(user_id):
    """Return user detail for confirm URL"""
    return reverse('user:user-read', args=[user_id])


def short_name_url(user_id):
    """Return user short name URL"""
    return reverse('user:user-shortname', args=[user_id])


def email_url(user_id):
    """Return user email URL"""
    return reverse('user:user-email', args=[user_id])


def password_url(user_id):
    """Return user password URL"""
    return reverse('user:user-password', args=[user_id])


def organized_event_url(user_id):
    """Return organized event URL"""
    return reverse('user:user-organizedEvents', args=[user_id])


def joined_event_url(user_id):
    """Return join event URL"""
    return reverse('user:user-joinedEvents', args=[user_id])


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.existed_user = UserFactory(
            email=fake.safe_email(),
            first_name=fake.first_name()
        )
        self.existed_user.is_guide = True
        self.existed_user.save()
        self.event = EventFactory(
            organizer=self.existed_user,
            event_time=make_aware(datetime.datetime.now())
        )
        self.participant = ParticipantFactory(
            event=self.event,
            user=self.existed_user
        )
        self.client = APIClient()

    def test_retrieve_designated_user(self):
        """Test retrieving a user"""
        url = show_user_url(self.existed_user.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user = get_user_model().objects.get(pk=res.data['id'])
        expected_json_dict = {
            'id': user.id,
            'short_name': user.first_name,
            'introduction': user.introduction,
            'icon_url': user.icon_url,
            'is_guide': user.is_guide
        }
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_retrieve_designated_user_for_update(self):
        """Test retrieving a user for update"""
        url = detail_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user = get_user_model().objects.get(pk=res.data['id'])
        expected_json_dict = {
            'id': user.id,
            'first_name': user.first_name,
            'family_name': user.family_name,
            'introduction': user.introduction,
            'icon_url': user.icon_url,
            'is_guide': user.is_guide,
        }
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_retrieve_organized_event(self):
        """Test retrieving organized events"""
        url = organized_event_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    'id': self.event.id,
                    'title': self.event.title,
                    'image': self.event.image_url,
                    'event_time': self.event.event_time
                    .strftime('%Y-%m-%d %H:%M:%S'),
                    'address': self.event.address,
                    "participant_count": 1
                }
            ]
        }
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_retrieve_organized_event_pagination(self):
        """Test retrieving organized events"""
        count = 0
        while count < 10:
            EventFactory(organizer=self.existed_user)
            count += 1

        url = organized_event_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 10)

        res = self.client.get(url, {'page': 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_retrieve_joined_event(self):
        """Test retrieving joined events"""
        url = joined_event_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    'id': self.event.id,
                    'title': self.event.title,
                    'image': self.event.image_url,
                    'event_time': self.event.event_time
                    .strftime('%Y-%m-%d %H:%M:%S'),
                    'address': self.event.address,
                    "participant_count": 1
                }
            ]
        }
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_retrieve_joined_event_pagination(self):
        """Test retrieving joined events"""
        count = 0
        while count < 10:
            ParticipantFactory(
                event=EventFactory(organizer=self.existed_user),
                user=self.existed_user
            )
            count += 1

        url = joined_event_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 10)

        res = self.client.get(url, {'page': 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_retrieve_user_email_by_unauthorized_user(self):
        """Test false retrieving user e-mail by unauthorized user"""
        url = email_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_by_unauthorized_user(self):
        """Test false updating the user profile by unauthorized user"""
        url = detail_url(self.existed_user.id)
        res = self.client.patch(url, {'first_name': 'firstname'})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_event_by_unauthorized_user(self):
        """Test false logically deleting the user by unauthenticated user"""
        url = detail_url(self.existed_user.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = UserFactory(email=fake.safe_email())
        self.another_user = UserFactory(email=fake.safe_email())
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.event = EventFactory(organizer=self.user)
        self.participant = ParticipantFactory(
            event=self.event, user=self.user
        )
        self.event_comment = EventCommentFactory(
            event=self.event, user=self.user
        )

    def test_retrieve_designated_user_short_name(self):
        """Test retrieving a user short name"""
        url = short_name_url(self.user.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertJSONEqual(res.content, {'short_name': 'noname'})

        familyName = 'family'
        self.user.family_name = familyName
        self.user.save()

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertJSONEqual(res.content, {'short_name': familyName})

        firstName = 'first'
        self.user.first_name = firstName
        self.user.save()

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertJSONEqual(res.content, {'short_name': firstName})

    def test_retrieve_user_email(self):
        """Test success retrive user e-mail"""
        url = email_url(self.user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)

    def test_update_user_email(self):
        """Test success updating the user e-mail"""
        email = fake.safe_email()
        url = email_url(self.user.id)
        res = self.client.patch(url, {'email': email})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_user = get_user_model().objects.latest('updated_at')
        self.assertEqual(email, updated_user.email)

    def test_full_update_user_profile(self):
        """Test full updating the user profile for authenticated user"""
        change_first_name = fake.first_name()
        change_family_name = fake.last_name()
        change_introduction = fake.text(max_nb_chars=1000)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            payload = {
                'first_name': change_first_name,
                'family_name': change_family_name,
                'introduction': change_introduction,
                'icon': ntf,
                'is_guide': True,
            }
            url = detail_url(self.user.id)
            res = self.client.patch(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, change_first_name)
        self.assertEqual(self.user.family_name, change_family_name)
        self.assertEqual(self.user.introduction, change_introduction)
        self.assertTrue(self.user.is_guide)
        self.assertTrue(os.path.exists(self.user.icon.path))

        self.user.icon.delete()

    def test_update_email_bad_request(self):
        """Test updating email with wrong method"""
        url = detail_url(self.user.id)
        res = self.client.patch(url, {'email': 'badrequest'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_bad_request(self):
        """Test updating password with wrong method"""
        url = detail_url(self.user.id)
        res = self.client.patch(url, {'password': 'badrequest'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = detail_url(self.user.id)
        res = self.client.patch(url, {'icon': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user_successful(self):
        """Test logically deleting the user"""
        self.user.is_guide = True
        self.user.save()

        url = detail_url(self.user.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.event.refresh_from_db()
        self.participant.refresh_from_db()
        self.event_comment.refresh_from_db()

        self.assertFalse(self.user.is_active)
        self.assertFalse(self.event.is_active)
        self.assertFalse(self.participant.is_active)
        self.assertFalse(self.event_comment.is_active)

    def test_retrieve_user_email_by_another_user(self):
        """Test false retrieving user e-mail by another user"""
        url = email_url(self.another_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_profile_by_another_user(self):
        """Test false updating the user profile by another user"""
        url = detail_url(self.another_user.id)
        res = self.client.patch(url, {'first_name': 'firstname'})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_by_another_user(self):
        """Test false logically deleting the user by another user"""
        url = detail_url(self.another_user.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
