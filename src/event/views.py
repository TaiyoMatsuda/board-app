from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import views, generics, viewsets, mixins, filters, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from core.models import EventComment, Participant, Event
from core.permissions import IsEventAttributeOwnerOnly, IsEventOwnerOnly, IsGuideOnly, IsValidEvent

from event import serializers


# class MultipleFieldLookupMixin(object):
#     """
#     Apply this mixin to any view or viewset to get multiple field filtering
#     based on a `lookup_fields` attribute, instead of the default single field filtering.
#     """
#     def get_object(self):
#         queryset = self.get_queryset()             # Get the base queryset
#         queryset = self.filter_queryset(queryset)  # Apply any filter backends
#         filter = {}
#         for field in self.lookup_fields:
#             if self.kwargs[field]: # Ignore empty fields.
#                 filter[field] = self.kwargs[field]
#         obj = get_object_or_404(queryset, **filter)  # Lookup the object
#         self.check_object_permissions(self.request, obj)
#         return obj


class EventCommentListSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100


class EventListSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10000000


class ListCreateParticipantView(generics.ListCreateAPIView):
    serializer_class = serializers.ListCreateParticipantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Participant.objects.filter(event=self.kwargs['pk'],status='1',is_active=True).order_by('updated_at')

    def post(self, request, *args, **kwargs):
        """Create a new participant in the system"""

        is_event_active = Event.objects.get(pk=kwargs['pk']).is_active
        if not is_event_active:
            return Response(status=status.HTTP_404_NOT_FOUND)

        event_status = Event.objects.get(pk=kwargs['pk']).status
        if event_status == '0' or event_status  == '2':
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def patch(self, request, *args, **kwargs):
        participant = get_object_or_404(self.queryset, event=kwargs['pk'], user=request.user.id)

        data = {}
        url = self.request.path
        if 'join' in url:
            data['status'] = 1
        elif 'cancel' in url:
            data['status'] = 0
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.UpdateParticipantSerializer(instance=participant, data=data, partial=True)
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
            permission_classes = [IsAuthenticatedOrReadOnly, IsValidEvent]
        else:
            permission_classes = [IsEventAttributeOwnerOnly]
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["comment_id"])
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
        serializer = serializers.ListCreateEventCommentSerializer(data=data)
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

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.BriefEventSerializer

        return serializers.EventSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticatedOrReadOnly]
        elif self.action == 'create':
            permission_classes = [IsAuthenticatedOrReadOnly, IsGuideOnly]
        else:
            permission_classes = [IsEventOwnerOnly]

        return [permission() for permission in permission_classes]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request):
        serializer = self.get_serializer(instance=self.queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = {
            'title': request.data['title'],
            'description': request.data['description'],
            'organizer': self.request.user.id,
            'image': None,
            'event_time': request.data['event_time'],
            'address': request.data['address'],
            'fee': request.data['fee'],
            'status': request.data['status'],
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        event = self.get_object()
        serializer = self.get_serializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        event = self.get_object()
        data = {
            'title': request.data['title'],
            'description': request.data['description'],
            'organizer': self.request.user.id,
            'image': request.data['image'],
            'event_time': request.data['event_time'],
            'address': request.data['address'],
            'fee': request.data['fee'],
            'status': request.data['status'],
        }
        serializer = self.get_serializer(instance=event, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """Logical Delete an event"""
        event = self.get_object()
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
