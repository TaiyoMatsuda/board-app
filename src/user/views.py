from rest_framework import generics, viewsets, mixins, authentication, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from core.models import User, Event, Participant
from core.permissions import IsUserOwnerOnly

from user import serializers
from event.serializers import BriefEventSerializer

class UserEventListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class UserViewSet(viewsets.ModelViewSet):
    """Manage User"""
    queryset = User.objects.filter(is_active=True)

    def get_permissions(self):
        """Return appropriate permission class"""
        if self.request.method == 'POST':
            permission_classes = [AllowAny]
        elif self.request.method == 'PATCH' or self.request.method == 'DELETE':
            permission_classes = [IsUserOwnerOnly]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateUserSerializer
        if self.action == 'email':
            return serializers.UserEmailSerializer
        if self.action == 'password':
            return serializers.UserPasswordSerializer
        if self.action == 'organizedEvents' or self.action == 'joinedEvents':
            return BriefEventSerializer
        return serializers.UserSerializer

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(methods=['patch'], detail=True, permission_classes=[IsUserOwnerOnly])
    def email(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, permission_classes=[IsUserOwnerOnly])
    def password(self, request, pk=None):
        if len(request.data) != 2:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if 'old_password' not in request.data or 'new_password' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = self.get_object()
        if user.password != request.data['old_password']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {'password': request.data['new_password']}
        serializer = self.get_serializer(instance=user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user_id = self.request.parser_context['kwargs']['pk']
        if self.action == 'organizedEvents':
            events = Event.objects.filter(organizer=user_id, is_active=True)
        elif self.action == 'joinedEvents':
            joined_event_id = Participant.objects.filter(user=user_id, status=1, is_active=True)
            events = Event.objects.filter(id__in=joined_event_id, is_active=True)

        page = self.paginate_queryset(events)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, pagination_class = UserEventListPagination)
    def organizedEvents(self, request, pk=None):
        return self.list(request)

    @action(methods=['get'], detail=True, pagination_class = UserEventListPagination)
    def joinedEvents(self, request, pk=None):
        return self.list(request)
        joined_event_id = Participant.objects.filter(user=user_id, status=1, is_active=True)
        joined_events = Event.objects.filter(id__in=joined_event_id, is_active=True)
        serializer = self.get_serializer(instance=joined_events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        #return self.list(request, *args, **kwargs)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Logical Delete an user"""
        event = self.get_object()
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
