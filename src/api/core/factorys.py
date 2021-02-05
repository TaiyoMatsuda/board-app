import datetime
import factory

from django.utils.timezone import now, localtime 
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from core.models import Event, EventComment, Participant


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = 'sampleuser@matsuda.com'
    password = 'testpass'


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = 'test title'
    description = 'test description'
    event_time = factory.LazyFunction(now)
    image = None
    address = 'test address'
    fee = 500
    status = Event.Status.PUBLIC

class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant