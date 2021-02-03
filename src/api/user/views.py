from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404

from core.models import User, Event, Participant
from core.permissions import IsUserOwnerOnly

from user import serializers


class UserViewSet(viewsets.GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    """Manage User"""
    queryset = User.objects.filter(is_active=True)

    def get_permissions(self):
        """Return appropriate permission class"""
        permission_classes = [IsAuthenticatedOrReadOnly]
        if self.request.method == 'POST':
            permission_classes = [AllowAny]
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            permission_classes = [IsUserOwnerOnly]

        if self.action == 'email':
            permission_classes = [IsUserOwnerOnly]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'confirm' or self.action == 'partial_update':
            return serializers.UpdateUserSerializer
        elif self.action == 'shortname':
            return serializers.UserShortNameSerializer
        elif self.action == 'email':
            return serializers.UserEmailSerializer
        elif self.action == 'organizedEvents' or self.action == 'joinedEvents':
            return serializers.UserEventsSerializer
        return serializers.UserSerializer

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(methods=['get'], detail=True)
    def confirm(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def shortname(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get', 'patch'], detail=True)
    def email(self, request, pk=None):
        user = self.get_object()
        if self.request.method == "GET":
            serializer = self.get_serializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user_id = self.request.parser_context['kwargs']['pk']
        if self.action == 'organizedEvents':
            events = Event.objects.filter(organizer=user_id, is_active=True)
        elif self.action == 'joinedEvents':
            joined_event_ids = Participant.objects.filter(
                user=user_id, status=1, is_active=True).values_list(
                    'event_id', flat=True)
            events = Event.objects.filter(
                id__in=joined_event_ids, status=1, is_active=True)

        page = self.paginate_queryset(events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def organizedEvents(self, request, pk=None):
        return self.list(request)

    @action(methods=['get'], detail=True)
    def joinedEvents(self, request, pk=None):
        return self.list(request)

    def update(self, request, *args, **kwargs):
        if 'email' in request.data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'password' in request.data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = self.get_object()
        serializer = self.get_serializer(
            instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Logical Delete an user"""
        event = self.get_object()
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
