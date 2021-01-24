from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

from rest_auth.views import LoginView, LogoutView, PasswordChangeView

router = DefaultRouter()
router.register('', views.UserViewSet)

app_name = 'user'

urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('password/change/', PasswordChangeView.as_view(),
         name='rest_password_change'),
    path('registration/', include('rest_auth.registration.urls')),
    path('', include(router.urls))
]
