import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import UserSerializer, AuthTokenSerializer


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

#     def test_password_too_short(self):
#         """Test that the password must be more than 5 characters"""
#         payload = {
#             'email': 'test@matsuda.com',
#             'password': 'pw'
#         }
#         serializer = UserSerializer(data=payload)

#         self.assertEqual(serializer.is_valid(), False)
#         self.assertCountEqual(serializer.errors.keys(), ['password'])

    def test_create_token_missing_email_field(self):
        """Test that email is required"""
        payload = {
            'email': 'one',
            'password': 'password'
        }
        serializer = AuthTokenSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['email'])

    def test_create_token_missing_password_field(self):
        """Test that password is required"""
        payload = {
            'email': 'test@matsuda.com',
            'password': ''
        }
        serializer = AuthTokenSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['password'])

    def test_create_token_non_field(self):
        """Test that field is invalid"""
        payload = {
            'email': 'test@matsuda.com',
            'password': 'password'
        }
        serializer = AuthTokenSerializer(data=payload)

        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['non_field_errors'])
