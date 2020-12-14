from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('', views.UserViewSet)

app_name = 'user'

urlpatterns = [
    path('<int:pk>/email', views.UpdateUserEmailView.as_view(), name='user_email'),
    path('<int:pk>/password', views.UserViewSet),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('', include(router.urls))
]
