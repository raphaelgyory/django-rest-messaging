# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals

from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.test import RequestFactory, TestCase
from rest_messaging.middleware import MessagingMiddleware
from rest_messaging.models import Participant


class TestMessagingMiddleware(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = User.objects.create(username='User')
        # we say the user is authenticated
        self.request.user.is_authenticated = lambda *args, **kwargs: True
        self.middleware = MessagingMiddleware()

    def test_middleware_new_participant(self):
        """ This test ensures the middleware creates the Participant corresponding to request.user, if not done yet. """
        # we ensure the cache is empty
        cache.clear()
        # we have no participant yet
        self.assertRaises(ObjectDoesNotExist, Participant.objects.get, id=self.request.user.id)
        with self.assertNumQueries(2):
            self.middleware.process_view(request=self.request, callback=None, callback_args=None, callback_kwargs=None)
        # the user has been created
        self.assertTrue(Participant.objects.get(id=self.request.user.id))
        self.assertEqual(self.request.rest_messaging_participant.id, self.request.user.id)
        # we rehit the middleware, rest_messaging_participant has been cached
        with self.assertNumQueries(0):
            self.middleware.process_view(request=self.request, callback=None, callback_args=None, callback_kwargs=None)

    def test_middleware_existing_participant(self):
        """ This test ensures the middleware creates the Participant corresponding to request.user, if not done yet. """
        # we ensure the cache is empty
        cache.clear()
        # we have a participant
        Participant.objects.create(id=self.request.user.id)
        with self.assertNumQueries(1):
            self.middleware.process_view(request=self.request, callback=None, callback_args=None, callback_kwargs=None)
        self.assertEqual(self.request.rest_messaging_participant.id, self.request.user.id)
        # we rehit the middleware, rest_messaging_participant has been cached
        with self.assertNumQueries(0):
            self.middleware.process_view(request=self.request, callback=None, callback_args=None, callback_kwargs=None)
