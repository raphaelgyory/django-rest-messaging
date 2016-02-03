# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.utils.six import BytesIO
from django.utils.timezone import now, timedelta
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from rest_messaging.models import Message, NotificationCheck, Participant, Participation, Thread


class TestScenario(APITestCase):
    """ Defaults for testing. """

    def setUp(self):
        # we create a user and a client
        password = "password"
        self.user = User(username="User")
        self.user.set_password(password)
        self.user.save()
        self.request_authenticated = APIRequestFactory()
        self.request_authenticated.user = self.user
        self.participant1 = Participant.objects.create(id=self.user.id)
        self.client_authenticated = APIClient()
        self.client_authenticated.login(username=self.user.username, password=password)
        self.client_unauthenticated = APIClient()
        # we create participants
        self.participant2 = Participant.objects.create(id=2)
        self.participant3 = Participant.objects.create(id=3)
        # we create a thread where all users are in
        self.thread1 = Thread.objects.create(name="All in!")
        self.participation1 = Participation.objects.create(participant=self.participant1, thread=self.thread1)
        self.participation2 = Participation.objects.create(participant=self.participant2, thread=self.thread1)
        self.participation3 = Participation.objects.create(participant=self.participant3, thread=self.thread1)
        # we create a thread where all users where in but one has left
        self.thread2 = Thread.objects.create(name="One has left")
        Participation.objects.create(participant=self.participant1, thread=self.thread2)
        Participation.objects.create(participant=self.participant2, thread=self.thread2)
        Participation.objects.create(participant=self.participant3, thread=self.thread2, date_left=now())
        # we create a thread where all only two users are in
        self.thread3 = Thread.objects.create(name="Two only are in")
        self.p1 = Participation.objects.create(participant=self.participant1, thread=self.thread3)
        self.p2 = Participation.objects.create(participant=self.participant3, thread=self.thread3)
        # we create a parasiting thread with people unrelated, to ensure it does not modify the counts
        self.participant4 = Participant.objects.create(id=4)
        self.participant5 = Participant.objects.create(id=5)
        self.participant6 = Participant.objects.create(id=6)
        self.thread_unrelated = Thread.objects.create(name="Unrelated")
        Participation.objects.create(participant=self.participant4, thread=self.thread_unrelated)
        Participation.objects.create(participant=self.participant5, thread=self.thread_unrelated)
        Participation.objects.create(participant=self.participant6, thread=self.thread_unrelated)
        # 1 message for thread 1, 2 for thread 2, etc.
        self.m11 = Message.objects.create(sender=self.participant1, thread=self.thread1, body="hi")
        self.m21 = Message.objects.create(sender=self.participant2, thread=self.thread2, body="hi")
        self.m22 = Message.objects.create(sender=self.participant1, thread=self.thread2, body="hi")
        self.m31 = Message.objects.create(sender=self.participant1, thread=self.thread3, body="hi")
        self.m32 = Message.objects.create(sender=self.participant3, thread=self.thread3, body="hi")
        self.m33 = Message.objects.create(sender=self.participant3, thread=self.thread3, body="hi")
        # a notification check
        # participant 1 has checked his notifications one day ago
        self.notification_check = NotificationCheck.objects.create(participant=self.participant1, date_check=now() - timedelta(days=1))
        # we mark some threads as read
        # participant 3 has read the 2 last messages, 1 only the first
        self.p2.date_last_check = now() - timedelta(days=1)
        self.p2.save()
        self.p1.date_last_check = now() - timedelta(days=2)
        self.p1.save()


def parse_json_response(json):
    """ parse the json response """
    rendered = JSONRenderer().render(json)
    stream = BytesIO(rendered)
    return JSONParser().parse(stream)
