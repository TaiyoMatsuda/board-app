from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.models import EventComment, Participant, Event


class ListCreateEventCommentSerializer(serializers.ModelSerializer):
    """Serializer for Participant objects"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )
    first_name = serializers.ReadOnlyField(source="user.first_name")
    icon = serializers.SerializerMethodField()
    brief_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = EventComment
        fields = ('id', 'event', 'user', 'first_name',
                  'icon', 'comment', 'brief_updated_at')

    def get_icon(self, participant):
        user = get_user_model().objects.get(pk=participant.user_id)
        return user.get_icon_url

    def get_brief_updated_at(sefl, instance):
        return instance.get_brief_updated_at


class ListCreateParticipantSerializer(serializers.ModelSerializer):
    """Serializer for Participant objects"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all())
    first_name = serializers.ReadOnlyField(source="user.first_name")
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ('event', 'user', 'first_name', 'icon')
        extra_kwargs = {'event': {'write_only': True}}

    def get_icon(self, participant):
        user = get_user_model().objects.get(pk=participant.user_id)
        return user.get_icon_url


class UpdateParticipantSerializer(serializers.ModelSerializer):
    """Serializer for Participant objects"""

    class Meta:
        model = Participant
        fields = ('status',)


class CreateEventSerializer(serializers.ModelSerializer):
    """Serialize for create event"""

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'organizer', 'image', 'event_time',
            'address', 'fee', 'status'
        )
        extra_kwargs = {'fee': {'default': 0}, }


class UpdateEventSerializer(serializers.ModelSerializer):
    """Serialize for update event"""

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'image', 'event_time', 'address',
            'fee', 'status'
        )
        extra_kwargs = {
            'fee': {'default': 0},
        }


class RetrieveEventSerializer(serializers.ModelSerializer):
    """Serialize for Event object"""
    organizer_first_name = serializers.ReadOnlyField(
        source="organizer.first_name")
    organizer_icon = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    event_time = serializers.SerializerMethodField()
    brief_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'organizer', 'organizer_first_name',
            'organizer_icon', 'image', 'event_time', 'address', 'fee',
            'status', 'brief_updated_at'
        )

    def get_organizer_icon(self, event):
        user = get_user_model().objects.get(pk=event.organizer.id)
        return user.get_icon_url

    def get_image(self, event):
        return event.get_image_url

    def get_event_time(sefl, event):
        return event.get_brief_event_time

    def get_brief_updated_at(sefl, event):
        return event.get_brief_updated_at


class BriefEventSerializer(serializers.ModelSerializer):
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
