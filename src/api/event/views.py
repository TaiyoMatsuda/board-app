from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

import datetime

from core.models import EventComment, Participant, Event
from core.permissions import (
    IsEventAttributeOwnerOnly, IsEventOwnerOnly, IsGuideOnly, IsValidEvent
)

from event import serializers


class EventListSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class EventCommentListSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class UnlimitedtPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = 'page_size'


class ListCreateParticipantView(generics.ListCreateAPIView):
    pagination_class = UnlimitedtPagination
    serializer_class = serializers.ListCreateParticipantSerializer

    def get_queryset(self):
        return Participant.objects.filter(
            event=self.kwargs['pk'], status='1', is_active=True
        ).order_by('updated_at')

    def post(self, request, *args, **kwargs):
        """Create a new participant in the system"""
        event = Event.objects.get(pk=kwargs['pk'])
        if not event.is_active:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if event.status == '0' or event.status == '2':
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = {
            'event': kwargs['pk'],
            'user': self.request.user.id
        }
        serializer = serializers.ListCreateParticipantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UpdateParticipantView(generics.UpdateAPIView):
    queryset = Participant.objects.all()
    serializer_class = serializers.UpdateParticipantSerializer

    def patch(self, request, *args, **kwargs):
        participant = get_object_or_404(
            self.queryset, event=kwargs['pk'], user=request.user.id)

        data = {}
        url = self.request.path
        if 'join' in url:
            data['status'] = 1
        elif 'cancel' in url:
            data['status'] = 0
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.UpdateParticipantSerializer(
            instance=participant, data=data, partial=True)
        if not serializer.is_valid():
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(status=status.HTTP_200_OK)


class EventCommentView(generics.GenericAPIView,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin
                       ):
    """Manage event comment in the database"""
    pagination_class = EventCommentListSetPagination
    serializer_class = serializers.ListCreateEventCommentSerializer
    queryset = EventComment.objects.filter(is_active=True)
    ordering = ['updated_at']

    def get_permissions(self):
        """Return appropriate permission class"""
        if self.request.method == 'GET' or self.request.method == 'POST':
            permission_class_list = [IsAuthenticatedOrReadOnly, IsValidEvent]
        else:
            permission_class_list = [IsEventAttributeOwnerOnly]
        return [permission() for permission in permission_class_list]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(),
                                pk=self.kwargs["comment_id"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {
            'event': kwargs['pk'],
            'user': self.request.user.id,
            'comment': request.data['comment']
        }
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *arts, **kwargs):
        """Logical Delete an event comment"""
        event_comment = self.get_object()
        event_comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class EventViewSet(viewsets.ModelViewSet):
    """Manage Event in the event"""
    pagination_class = EventListSetPagination
    queryset = Event.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            start = self.request.query_params['start'] + ' 00:00:00'
            end = self.request.query_params['end'] + ' 23:59:59'
            return Event.objects.filter(is_active=True,
                                        event_time__range=(start, end))

        return Event.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.BriefEventSerializer
        elif self.action == 'retrieve':
            return serializers.RetrieveEventSerializer
        elif self.action == 'create':
            return serializers.CreateEventSerializer
        else:
            return serializers.UpdateEventSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that
        this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_class_list = [IsAuthenticatedOrReadOnly]
        elif self.action == 'create':
            permission_class_list = [IsAuthenticatedOrReadOnly, IsGuideOnly]
        else:
            permission_class_list = [IsEventOwnerOnly]

        return [permission() for permission in permission_class_list]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request):
        query_params = self.request.query_params
        try:
            datetime.datetime.strptime(query_params['start'], "%Y-%m-%d")
            datetime.datetime.strptime(query_params['end'], "%Y-%m-%d")
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        events = self.get_queryset()
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        if request.data['organizer'] != str(self.request.user.id):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        event = self.get_object()
        serializer = self.get_serializer(instance=event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        event = self.get_object()
        if event.organizer.id != self.request.user.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance=event, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Logical Delete an event"""
        event = self.get_object()
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
