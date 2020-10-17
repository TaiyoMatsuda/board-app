import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
AUTH_URL = reverse('user:auth')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def get_user_by_json(**params):
    user = get_user_model().objects.get(email=params['email'])

    if len(str(user.icon)) == 0:
        expected_json_dict = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'introduction': user.introduction,
            'icon': None
        }
    else:
        expected_json_dict = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'introduction': user.introduction,
            'icon': 'http://testserver/media/' + str(user.icon)
        }

    return expected_json_dict


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@matsuda.com',
            'password': 'testpass'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        expected_json_dict = get_user_by_json(**res.data)
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@matsuda.com',
            'password': 'testpass'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@matsuda.com',
            'password': 'testpass'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invaid credetials are given"""
        create_user(email='test@matsuda.com', password='testpass')
        payload = {
            'email': 'test@matsuda.com',
            'password': 'worng'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_nouser(self):
        """Test that token is not created if user doesn't exit"""
        payload = {
            'email': 'test@matsuda.com',
            'password': 'testpass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(AUTH_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPiTests(TestCase):
    """Test API requests that require authhentication"""

    def setUp(self):
        self.user = create_user(
            email='test@matsuda.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""
        res = self.client.get(AUTH_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict = get_user_by_json(**res.data)

        self.assertJSONEqual(res.content, expected_json_dict)

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        res = self.client.post(AUTH_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_user_profile(self):
        """Test partial updating the user profile for authenticated user"""
        payload = {
            'password': 'newpassword123',
            'first_name': 'newfirstname',
            'last_name': 'newlastname'
        }
        res = self.client.patch(AUTH_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        expected_json_dict = get_user_by_json(**res.data)
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_full_update_user_profile(self):
        """Test full updating the user profile for authenticated user"""
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            payload = {
                'email': 'newemail@matsuda.com',
                'password': 'newpassword123',
                'first_name': 'firstname',
                'last_name': 'last_name',
                'is_active': True,
                'is_staff': True,
                'introduction': 'introductiontest',
                'icon': ntf
            }
            res = self.client.put(AUTH_URL, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        expected_json_dict = get_user_by_json(**res.data)
        self.assertJSONEqual(res.content, expected_json_dict)
        self.assertTrue(os.path.exists(self.user.icon.path))

        self.user.icon.delete()

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        res = self.client.patch(
            AUTH_URL,
            {'icon':'notimage'},
            format='multipart'
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
