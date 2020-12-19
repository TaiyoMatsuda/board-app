from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.models import EventComment, Participant, Event


class ListCreateEventCommentSerializer(serializers.ModelSerializer):
    """Serializer for Participant objects"""
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    first_name = serializers.ReadOnlyField(source="user.first_name")
    icon = serializers.SerializerMethodField()
    brief_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = EventComment
        fields = ('id', 'event', 'user', 'first_name', 'icon', 'comment', 'brief_updated_at')

    def get_icon(self, participant):
        user = get_user_model().objects.get(pk=participant.user_id)
        return user.get_icon_url

    def get_brief_updated_at(sefl, instance):
        return instance.get_brief_updated_at


class ListCreateParticipantSerializer(serializers.ModelSerializer):
    """Serializer for Participant objects"""
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    first_name = serializers.ReadOnlyField(source="user.first_name")
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = ('event', 'user', 'first_name', 'icon')
        extra_kwargs = {
            'event': {'write_only': True}
        }

    def get_icon(self, participant):
        user = get_user_model().objects.get(pk=participant.user_id)
        return user.get_icon_url


class UpdateParticipantSerializer(serializers.ModelSerializer):
    """Serializer for Participant objects"""

    class Meta:
        model = Participant
        fields = ('status',)

class EventSerializer(serializers.ModelSerializer):
    """Serialize for Event object"""
    organizer_id = serializers.ReadOnlyField(source="organizer.id")
    organizer_first_name = serializers.ReadOnlyField(source="organizer.first_name")
    organizer_icon = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    event_comment_list = ListCreateEventCommentSerializer(read_only=True)
    participant_list = ListCreateParticipantSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField()
    brief_updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'organizer', 'organizer_id',
            'organizer_first_name', 'organizer_icon', 'image', 'event_time',
            'address', 'fee', 'status', 'event_comment_list', 'participant_list',
            'participant_count', 'brief_updated_at'
        )
        extra_kwargs = {
            'organizer': {'write_only': True, 'required': False},
            'fee': {'default': 0},
        }

    def get_image(self, event):
        return event.get_image_url

    def get_organizer_icon(self, event):
        user = get_user_model().objects.get(pk=event.organizer.id)
        return user.get_icon_url

    def get_participant_count(self, event):
        participant = Participant.objects.filter(event_id=event.id, status= '1', is_active=True)
        return participant.count()

    def get_brief_updated_at(sefl, event):
        return event.get_brief_updated_at


class RetrieveEventSerializer(serializers.ModelSerializer):
    """Serialize for Event object"""
    organizer_first_name = serializers.ReadOnlyField(source="organizer.first_name")
    organizer_icon = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'organizer', 'organizer_first_name',
            'organizer_icon', 'image', 'event_time', 'address', 'fee', 'status',
            # 'event_comment_list', 'participant_list',
            # 'participant_count', 'brief_updated_at'
        )

    # organizer_id = serializers.ReadOnlyField(source="organizer.id")

    # image = serializers.SerializerMethodField()
    # event_comment_list = ListCreateEventCommentSerializer(read_only=True)
    # participant_list = ListCreateParticipantSerializer(read_only=True)
    # participant_count = serializers.SerializerMethodField()
    # brief_updated_at = serializers.SerializerMethodField()
    #
    # class Meta:
    #     model = Event
    #     fields = (
    #         'id', 'title', 'description', 'organizer_id', 'organizer_first_name',
    #         'organizer_icon', 'image', 'event_time', 'address', 'fee', 'status',
    #         'event_comment_list', 'participant_list',
    #         'participant_count', 'brief_updated_at'
    #     )
    #
    def get_image(self, event):
        return event.get_image_url

    def get_organizer_icon(self, event):
        user = get_user_model().objects.get(pk=event.organizer.id)
        return user.get_icon_url

    def get_participant_count(self, event):
        participant = Participant.objects.filter(event_id=event.id, status= '1', is_active=True)
        return participant.count()

    def get_brief_updated_at(sefl, event):
        return event.get_brief_updated_at


class BriefEventSerializer(serializers.ModelSerializer):
    """Serialize for Event object"""
    image = serializers.SerializerMethodField()
    event_time = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'image', 'event_time', 'address', 'participant_count'
        )

    def get_image(self, event):
        return event.get_image_url

    def get_event_time(self, event):
        return event.get_brief_event_time

    def get_participant_count(self, event):
        participant = Participant.objects.filter(event_id=event.id, status= '1', is_active=True)
        return participant.count()
