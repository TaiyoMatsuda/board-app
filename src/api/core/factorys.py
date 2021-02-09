import datetime
import factory

from faker import Faker

from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from core.models import Event, EventComment, Participant


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = fake.safe_email()
    password = 'testpass'


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    title = fake.text(max_nb_chars=255)
    description = fake.text(max_nb_chars=2000)
    event_time = factory.LazyFunction(now)
    image = fake.image_url()
    address = fake.address()
    fee = 500
    status = Event.Status.PUBLIC


class EventCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventComment

    comment = fake.text(max_nb_chars=500)


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant