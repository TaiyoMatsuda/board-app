from django.urls import path, inclued
from rest_framework.routers import DefaultRouter

from event import views


router = DefaultRouter()
router.register('event_comment', views.EventCommentViewSet)
router.register('organizer', views.OrganizerViewSet)
router.register('event', views.EventViewSet)
