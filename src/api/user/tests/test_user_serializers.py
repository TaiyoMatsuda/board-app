import datetime

from faker import Faker

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import Event
from core.factorys import UserFactory, EventFactory
from user.serializers import (ShowUserSerializer, UserEmailSerializer,
                              UserEventsSerializer, UserSerializer,
                              UserShortNameSerializer)


fake = Faker()


class UserSerializerApiTests(TestCase):
    """Test user serializer API"""

    def setUp(self):
        self.email = fake.safe_email()
        self.organizer = UserFactory(email=self.email)
        self.organizer.first_name = fake.first_name()
        self.organizer.family_name = fake.last_name()
        self.organizer.introduction = fake.text(max_nb_chars=1000)
        self.organizer.is_guide = True
        self.organizer.save()

        self.event = EventFactory(
            organizer=self.organizer,
            event_time=make_aware(datetime.datetime.now())            
        )

    def test_retrieve_user_for_update(self):
        """Test retrieve user fields for update"""
        serializer = UserSerializer(instance=self.organizer)
        expected_dict = {
            'id': self.organizer.id,
            'first_name': self.organizer.first_name,
            'family_name': self.organizer.family_name,
            'introduction': self.organizer.introduction,
            'icon_url': '/static/images/no_user_image.png',
            'is_guide': self.organizer.is_guide
        }
        self.assertEqual(serializer.data, expected_dict)

    def test_retrieve_user_successful(self):
        """Test retrieve user fields successful"""
        serializer = ShowUserSerializer(instance=self.organizer)
        expected_dict = {
            'id': self.organizer.id,
            'short_name': self.organizer.first_name,
            'introduction': self.organizer.introduction,
            'icon_url': '/static/images/no_user_image.png',
            'is_guide': self.organizer.is_guide
        }
        self.assertEqual(serializer.data, expected_dict)

    def test_retrieve_designated_user_short_name(self):
        """Test retrieving a user short name"""
        noname_user = UserFactory(email=fake.safe_email())

        serializer = UserShortNameSerializer(instance=noname_user)
        self.assertEqual(serializer.data, {'short_name': 'noname'})

        familyName = 'family'
        noname_user.family_name = familyName
        noname_user.save()
        serializer = UserShortNameSerializer(instance=noname_user)
        self.assertEqual(serializer.data, {'short_name': familyName})

        firstName = 'first'
        noname_user.first_name = firstName
        noname_user.save()
        serializer = UserShortNameSerializer(instance=noname_user)
        self.assertEqual(serializer.data, {'short_name': firstName})

    def test_update_user_successful(self):
        """Test update user fields successful"""
        data = {'is_guide': False}
        serializer = UserSerializer(instance=self.organizer, data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(serializer.data['is_guide'], data['is_guide'])

    def test_long_user_first_name_validate(self):
        """Test retrieve user fields successful"""
        long_first_name = "long_first_name " * 500
        data = {'first_name': long_first_name}
        serializer = UserSerializer(instance=self.organizer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['first_name'])

    def test_long_user_family_name_validate(self):
        """Test retrieve user fields successful"""
        long_family_name = "long_family_name " * 500
        data = {'family_name': long_family_name}
        serializer = UserSerializer(instance=self.organizer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['family_name'])

    def test_long_introduction_validate(self):
        """Test retrieve user fields successful"""
        long_introduction = "logn_introduction " * 500
        data = {'introduction': long_introduction}
        serializer = UserSerializer(instance=self.organizer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['introduction'])

    def test_not_updating_user_icon_validate(self):
        """Test retrieve user fields successful"""
        data = {'icon': 1}
        serializer = UserSerializer(instance=self.organizer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['icon'])

    def test_not_updating_is_guide_with_not_boolean(self):
        """Test updating is_guide with not boolean"""
        data = {'is_guide': 'test'}
        serializer = UserSerializer(instance=self.organizer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['is_guide'])

    def test_updating_other_field_with_userserialize(self):
        """Test not updating other fields"""
        serializer = UserSerializer(
            instance=self.organizer,
            data={'email': fake.safe_email()}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertEqual(self.organizer.email, self.email)

    def test_retrieve_user_email_successful(self):
        """Test retrieving user email successful"""
        serializer = UserEmailSerializer(instance=self.organizer)
        expected_dict = {'email': self.email}
        self.assertEqual(serializer.data, expected_dict)

    def test_update_user_email_successful(self):
        """Test validate user email successful"""
        data = {'email': fake.safe_email()}
        serializer = UserEmailSerializer(instance=self.organizer, data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(serializer.data, data)

    def test_update_user_email_with_not_email_format(self):
        """Test validate user email false with not email format"""
        data = {'email': 'organizer_changed'}
        serializer = UserEmailSerializer(instance=self.organizer, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertCountEqual(serializer.errors.keys(), ['email'])

    def test_retrieve_user_events_successful(self):
        """Test retrieve user events successful"""
        events = Event.objects.filter(
            organizer=self.organizer.id, is_active=True)
        serializer = UserEventsSerializer(instance=events, many=True)

        expected_dict = {
            'id': self.event.id,
            'title': self.event.title,
            'image': self.event.image_url,
            'event_time': self.event.event_time.strftime('%Y-%m-%d %H:%M:%S'),
            'address': self.event.address,
            'participant_count': 0
        }
        self.assertEqual(dict(serializer.data[0]), expected_dict)