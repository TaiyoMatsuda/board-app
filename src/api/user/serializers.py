from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import Participant, Event


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'first_name', 'family_name', 'introduction',
            'icon_url', 'is_guide', 'icon'
        )
        extra_kwargs = {'icon': {'write_only': True}}

    def get_icon_url(self, user):
        return user.get_icon_url


class UserEmailSerializer(serializers.ModelSerializer):
    """Serializer for the user email object"""

    class Meta:
        model = get_user_model()
        fields = ('email',)


class UserEventsSerializer(serializers.ModelSerializer):
    """Serialize for brief event object"""
    image = serializers.SerializerMethodField()
    event_time = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'image', 'event_time', 'address',
            'participant_count'
        )

    def get_image(self, event):
        return event.get_image_url

    def get_event_time(self, event):
        return event.get_brief_event_time

    def get_participant_count(self, event):
        participant = Participant.objects.filter(
            event_id=event.id, status='1', is_active=True)
        return participant.count()
