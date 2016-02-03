# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from rest_framework import serializers
from rest_messaging.compat import compat_serializer_attr, compat_serializer_method_field
from rest_messaging.models import Message, NotificationCheck, Thread


class ThreadSerializer(serializers.ModelSerializer):

    participants = compat_serializer_method_field("get_participants")

    class Meta:
        model = Thread
        fields = ('id', 'name', 'participants')

    def __init__(self, *args, **kwargs):
        # Don't pass the 'callback' arg up to the superclass
        self.callback = kwargs.pop('callback', None)
        # Instantiate the superclass normally
        super(ThreadSerializer, self).__init__(*args, **kwargs)

    def get_participants(self, obj):
        """ Allows to define a callback for serializing information about the user. """
        # we set the many to many serialization to False, because we only want it with retrieve requests
        if self.callback is None:
            return [participant.id for participant in obj.participants.all()]
        else:
            # we do not want user information
            return self.callback(obj)


class SimpleMessageSerializer(serializers.ModelSerializer):
    """ Returns the messages without complementary information. """

    class Meta:
        model = Message
        fields = ('id', 'body', 'sender', 'thread', 'sent_at')


class ComplexMessageSerializer(serializers.ModelSerializer):

    is_notification = compat_serializer_method_field("get_is_notification")
    readers = compat_serializer_method_field("get_readers")

    class Meta:
        model = Message
        fields = ('id', 'body', 'sender', 'thread', 'sent_at', 'is_notification', 'readers')

    def get_is_notification(self, obj):
        """ We say if the message should trigger a notification """
        try:
            o = compat_serializer_attr(self, obj)
            return o.is_notification
        except Exception:
            return False

    def get_readers(self, obj):
        """ Return the ids of the people who read the message instance. """
        try:
            o = compat_serializer_attr(self, obj)
            return o.readers
        except Exception:
            return []


class MessageNotificationCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationCheck
