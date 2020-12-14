import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

USER_URL = reverse('user:user-list')
TOKEN_URL = reverse('user:token')

def detail_url(user_id):
    """Return user detail URL"""
    return reverse('user:user-detail', args=[user_id])

def email_url(user_id):
    """Return user email URL"""
    return reverse('user:user_email', args=[user_id])

def password_url(user_id):
    """Return user password URL"""
    return reverse('user:user_email', args=[user_id])

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def get_user_by_json(**params):
    user = get_user_model().objects.get(email=params['email'])
    expected_json_dict = {
        'id': user.id,
        'first_name': user.first_name,
        'family_name': user.family_name,
        'email': user.email,
        'introduction': user.introduction,
        'icon_url': user.get_icon_url,
        'is_guide': user.is_guide,
        }

    return expected_json_dict


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.password = 'testpass'
        self.existed_user = create_user(
            email='existed_user@matsuda.com',
            password=self.password,
            first_name='existed'
        )
        self.client = APIClient()

    def test_retrieve_designated_user(self):
        """Test that authentication is required for users"""
        url = detail_url(self.existed_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        expected_json_dict = get_user_by_json(**res.data)
        self.assertJSONEqual(res.content, expected_json_dict)

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        email = 'test@matsuda.com'
        payload = {
            'email': email,
            'password': 'testpass'
        }
        res = self.client.post(USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.latest('created_at')
        self.assertEqual(user.email, email)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': self.existed_user.email,
            'password': self.existed_user.password
        }
        res = self.client.post(USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': self.existed_user.email,
            'password': self.password
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invaid credetials are given"""
        payload = {
            'email': self.existed_user.email,
            'password': 'worng'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exit"""
        payload = {
            'email': 'test@matsuda.com',
            'password': 'testpass'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserAPiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@matsuda.com',
            password='testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_update_user_email(self):
        """Test success updating the user e-mail"""
        email = 'change_email@matsuda.com'
        url = email_url(self.user.id)
        res = self.client.patch(url, {'email': email})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], email)

    def test_update_user_password(self):
        """Test success updating the user e-mail"""
        url = password_url(self.user.id)
        res = self.client.patch(url, {'password': 'change_password'})
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        password = get_user_model().objects.latest('updated_at').password
        self.assertEqual(self.user.password, password)

    def test_full_update_user_profile(self):
        """Test full updating the user profile for authenticated user"""
        change_first_name = 'firstname'
        change_family_name = 'family_name'
        change_introduction = 'introduction'
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

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = detail_url(self.user.id)
        res = self.client.patch(url, {'icon':'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
