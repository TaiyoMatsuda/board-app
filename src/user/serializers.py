from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from event.serializers import BriefEventSerializer

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password')

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'first_name', 'family_name', 'introduction',
            'icon_url', 'is_guide', 'icon'
            )
        extra_kwargs = {'icon': {'write_only': True}}

    def get_icon_url(self, user):
        return user.get_icon_url


class UserEmailSerializer(serializers.ModelSerializer):
    """Serializer for the user email object"""

    class Meta:
        model = get_user_model()
        fields = ('email',)


class UserPasswordSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('password',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}


class UserEventsSerializer(serializers.Serializer):
    """Serializer for the users object"""

    class Meta:
        list_serializer_class = BriefEventSerializer


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
