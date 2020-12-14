from django.urls import path, include
from rest_framework.routers import DefaultRouter

from event import views


router = DefaultRouter()
router.register('', views.EventViewSet)

app_name = 'event'

urlpatterns = [
    path('<int:pk>/participants', views.ListCreateParticipantView.as_view(), name='listCreateParticipant'),
    path('<int:pk>/participants/cancel', views.UpdateParticipantView.as_view(), name='cancelParticipant'),
    path('<int:pk>/participants/join', views.UpdateParticipantView.as_view(), name='joinParticipant'),
    path('<int:pk>/comments', views.EventCommentView.as_view(), name='eventComment'),
    path('<int:event_id>/comments/<int:comment_id>', views.EventCommentView.as_view(), name='deleteComment'),
    path('', include(router.urls))
]
