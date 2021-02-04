from rest_framework.permissions import BasePermission

from core.models import Event


class IsEventAttributeOwnerOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user == obj.user)


class IsEventOwnerOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user == obj.organizer)


class IsUserOwnerOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user == obj)


class IsGuideOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_guide


class IsValidEvent(BasePermission):

    def has_permission(self, request, view):
        pk = request.parser_context['kwargs']['pk']
        event = Event.objects.get(pk=pk)
        return event.is_valid_comment()
