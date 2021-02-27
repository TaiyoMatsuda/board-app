from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import Event, EventComment, Participant


class ListEventCommentSerializer(serializers.ModelSerializer):
    """Serializer for List EventComment"""
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )
    first_name = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    brief_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = EventComment
        fields = ('id', 'event', 'user', 'first_name', 'icon',
                  'comment', 'status', 'brief_updated_at')

    def get_first_name(self, inastance):
        user = get_user_model().objects.get(pk=inastance.user_id)
        return user.short_name

    def get_icon(self, inastance):
        user = get_user_model().objects.get(pk=inastance.user_id)
        return user.icon_url

    def get_comment(self, inastance):
        return inastance.display_comment

    def get_brief_updated_at(self, instance):
        return instance.brief_updated_at


class CreateEventCommentSerializer(serializers.ModelSerializer):
    """Serializer for Create EventComment"""

    class Meta:
        model = EventComment
        fields = ('event', 'user', 'comment')


class UpdateEventCommentSerializer(serializers.ModelSerializer):
    """Serializer for Update EventComment"""

    class Meta:
        model = Participant
        fields = ('status',)


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
        return user.icon_url


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
    organizer_full_name = serializers.ReadOnlyField(
        source="organizer.full_name")
    organizer_icon = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    event_time = serializers.SerializerMethodField()
    brief_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'organizer', 'organizer_full_name',
            'organizer_icon', 'image', 'event_time', 'address', 'fee',
            'status', 'brief_updated_at'
        )

    def get_organizer_icon(self, event):
        user = get_user_model().objects.get(pk=event.organizer.id)
        return user.icon_url

    def get_image(self, event):
        return event.image_url

    def get_event_time(self, event):
        return event.brief_event_time

    def get_brief_updated_at(self, event):
        return event.brief_updated_at


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
        return event.image_url

    def get_event_time(self, event):
        return event.brief_event_time

    def get_participant_count(self, event):
        participant = Participant.objects.filter(
                event_id=event.id,
                status=Participant.Status.JOIN.value,
                is_active=True
            )
        return participant.count()
