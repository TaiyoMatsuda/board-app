import uuid
import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from django.utils import timezone
from django.utils.timezone import localtime


def user_icon_file_path(instance, filename):
    """Generate file path for new user icon"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/user/', filename)


def event_image_file_path(instance, filename):
    """Generate file path for new event image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/event/', filename)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and saves a new super user"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suppors using email instead of username"""

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    family_name = models.CharField(_('family name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_guide = models.BooleanField(_('guide status'), default=False)
    introduction = models.TextField(blank=True, max_length=1000)
    icon = models.ImageField(
        null=True,
        blank=True,
        upload_to=user_icon_file_path
    )
    created_at = models.DateTimeField(_('created_at'), default=timezone.now)
    updated_at = models.DateTimeField(_('update_at'), auto_now=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'm_user'

    def get_short_name(self):
        """Return the short name for the user"""
        return self.first_name

    @property
    def get_icon_url(self):
        if self.icon and hasattr(self.icon, 'url'):
            return self.icon.url
        else:
            return "/static/images/no_user_image.png"

    def delete(self):
        """Logical delete the user"""
        self.is_active = false
        self.save()
        return self


class Event(models.Model):
    """Event object"""
    class Meta:
        db_table = 't_event'
        ordering = ['event_time']

    STATUS = (
        ('0', 'Private'),
        ('1', 'Publish'),
        ('2', 'Cancel'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=event_image_file_path
    )
    event_time = models.DateTimeField(null=False)
    address = models.CharField(null=False, max_length=255)
    fee = models.IntegerField(
        null=False,
        blank=False,
        default=0,
        validators=[MinValueValidator(0),
                    MaxValueValidator(100000)]
    )
    status = models.CharField(max_length=10, choices=STATUS, default='0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        else:
            return "/static/images/no_event_image.png"

    @property
    def get_brief_event_time(self):
        """Return the event time except millisecond"""
        return localtime(self.event_time).strftime('%Y-%m-%d %H:%M:%S')

    @property
    def get_brief_updated_at(self):
        """Return the update time except millisecond"""
        return localtime(self.updated_at).strftime('%Y-%m-%d %H:%M:%S')

    def delete(self):
        """Logical delete the user"""
        self.is_active = False
        self.save()
        return self


class EventComment(models.Model):
    """EventComment to be used for an Event"""
    class Meta:
        db_table = 't_event_comment'
        ordering = ['updated_at']

    event = models.ForeignKey(
        'Event',
        to_field='id',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE,
    )
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.comment

    @property
    def get_brief_updated_at(self):
        """Return the update time except millisecond"""
        return localtime(self.updated_at).strftime('%Y-%m-%d %H:%M:%S')

    def delete(self):
        """Logical delete the user"""
        self.is_active = False
        self.save()
        return self


class Participant(models.Model):
    """Participant to be used for an Event"""
    class Meta:
        db_table = 't_participant'
        ordering = ['updated_at']

    STATUS = (
        ('0', 'Cancel'),
        ('1', 'Join'),
    )

    event = models.ForeignKey(
        Event,
        to_field='id',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        to_field='id',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS, default='1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_short_name()

    def delete(self):
        self.is_active = False
        self.save()
        return self
