# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_messaging.compat import compat_serializer_method_field
from rest_messaging.models import Thread
from rest_messaging.serializers import SimpleMessageSerializer, ThreadSerializer
from .models import Profile
from .utils import TestScenario


def _thread_serializer_callback(thread_instance):
    """ Shows how ThreadSerializer can get access to data about the users, beyond their simple ids. """
    # we get all the participants' ids
    participants_ids = [participant.id for participant in thread_instance.participants.all()]
    # we can run the query we want usng this ids
    # here we want the users and related information
    users = User.objects.filter(id__in=participants_ids).select_related('profile')
    # we call our custom serializer
    serialized = UserProfileSerializer(users, many=True)
    return serialized.data


class UserProfileSerializer(serializers.ModelSerializer):
    """ Serializer for testing purpose only (for the ThreadSerializer callback). """

    image = compat_serializer_method_field('get_image')
    contact = compat_serializer_method_field('get_contact')

    class Meta:
        model = User
        fields = ('id', 'username', 'image', 'contact')

    def get_image(self, obj):
        return obj.profile.image

    def get_contact(self, obj):
        return obj.profile.contact


class TestThreadSerializer(TestScenario):

    def setUp(self):
        super(TestThreadSerializer, self).setUp()
        # we create users and profiles in order to serialize them
        self.user2 = User.objects.create(username="User2")
        self.profile = Profile.objects.create(user=self.user, image="/path/to/image.jpeg", contact="Hello!")
        self.profile2 = Profile.objects.create(user=self.user2, image="/path/to/image.jpeg", contact="Hello!")

    def test_participants(self):
        """ Test for the serializer callback """
        # by default, we get a list of ids
        serializer = ThreadSerializer(self.thread1, callback=getattr(settings, 'REST_MESSAGING_SERIALIZE_PARTICIPANTS_CALLBACK', None))
        self.assertEqual(set(serializer.data["participants"]), set([self.participant1.id, self.participant2.id, self.participant3.id]))  # we do not care about ordering

    def test_participants_callback(self):
        """ Test for the serializer callback """
        # we can override the serializer and provide a callback
        # here the callback ensures we do not run n queries
        # we recuperate thread1 and run related queries, to be able to check the count later
        tread1 = Thread.objects.filter(id=self.thread1.id).prefetch_related('participants')[0]
        with self.assertNumQueries(1):
            serializer = ThreadSerializer(tread1, callback=_thread_serializer_callback)
            self.assertEqual(serializer.data["participants"][0]["username"], self.user.username)
            self.assertEqual(serializer.data["participants"][0]["image"], self.user.profile.image)
            self.assertEqual(serializer.data["participants"][1]["username"], self.user2.username)
            self.assertEqual(serializer.data["participants"][1]["image"], self.user2.profile.image)


class TestSimpleMessageSerializer(TestScenario):

    def test_num_queries(self):
        with self.assertNumQueries(0):
            # we ensure the serializer does not trigger additional queries
            serializer = SimpleMessageSerializer(self.m11)
            self.assertEqual(serializer.data["sender"], self.participant1.id)
