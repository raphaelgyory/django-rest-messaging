# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals

from django.conf import settings
from django.utils.timezone import now
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_messaging.compat import compat_get_paginated_response, compat_get_request_data, compat_pagination_messages, compat_serializer_check_is_valid, compat_thread_serializer_set, compat_perform_update
from rest_messaging.models import Message, NotificationCheck, Participant, Participation, Thread
from rest_messaging.permissions import IsInThread
from rest_messaging.serializers import MessageNotificationCheckSerializer, ComplexMessageSerializer, SimpleMessageSerializer, ThreadSerializer
import json


class ThreadView(mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    """
    The ThreadView allow us to create threads, and add/remove people to/from them.
    It does not list the messages belonging to the thread.
    """
    queryset = Thread.objects.all().prefetch_related('participants')
    serializer_class = ThreadSerializer
    permission_classes = (IsInThread,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ThreadSerializer(instance, callback=getattr(settings, 'REST_MESSAGING_SERIALIZE_PARTICIPANTS_CALLBACK', None), context={'request': request})  # self.get_serializer will raise an error in DRF 2.4
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """ We ensure the Thread only involves eligible participants. """
        serializer = self.get_serializer(data=compat_get_request_data(request))
        compat_serializer_check_is_valid(serializer)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        participants_ids = json.loads(compat_get_request_data(self.request).get('participants'))
        thread = Thread.managers.get_or_create_thread(self.request, compat_get_request_data(self.request).get('name'), *participants_ids)
        setattr(serializer, compat_thread_serializer_set(), thread)

    def update(self, request, *args, **kwargs):
        participants_ids = compat_get_request_data(self.request).getlist('participants', [])
        if len(participants_ids) > 0:
            # we warn the user he cannot update the participants here
            return Response("Participant updates not allowed by this method.", status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=compat_get_request_data(request), partial=partial)
        compat_serializer_check_is_valid(serializer)
        try:
            self.perform_update(serializer)
        except:
            compat_perform_update(self, serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_participants(self, request, pk=None):
        # we get the thread and check for permission
        thread = Thread.objects.get(id=pk)
        self.check_object_permissions(request, thread)
        # we get the participants and add them
        participants_ids = json.loads(compat_get_request_data(self.request).get('participants'))
        thread.add_participants(request, *participants_ids)
        # we return the thread
        serializer = self.get_serializer(thread)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        # we get the thread and check for permission
        thread = Thread.objects.get(id=pk)
        self.check_object_permissions(request, thread)
        # we get the participant
        participant_id = compat_get_request_data(self.request).get('participant')
        participant = Participant.objects.get(id=participant_id)
        # we remove him if thread.remove_participant allows us to
        try:
            thread.remove_participant(request, participant)
            # we return the thread
            serializer = self.get_serializer(thread)
            return Response(serializer.data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def get_removable_participants_ids(self, request, pk=None):
        # we get the thread and check for permission
        thread = Thread.objects.get(id=pk)
        self.check_object_permissions(request, thread)
        # we get the removable participants
        removable_participants_ids = thread.get_removable_participants_ids(request)
        # we remove him if thread.remove_participant allows us to
        try:
            return Response({'participants': removable_participants_ids})
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_thread_as_read(self, request, pk=None):
        """ Pk is the pk of the Thread to which the messages belong. """
        # we get the thread and check for permission
        thread = Thread.objects.get(id=pk)
        self.check_object_permissions(request, thread)
        # we save the date
        try:
            participation = Participation.objects.get(thread=thread, participant=request.rest_messaging_participant)
            participation.date_last_check = now()
            participation.save()
            # we return the thread
            serializer = self.get_serializer(thread)
            return Response(serializer.data)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@compat_pagination_messages
class MessageView(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """ The view only lists and creates. """

    queryset = Message.objects.none()
    serializer_class = ComplexMessageSerializer
    permission_classes = (IsInThread,)

    def get_queryset(self):
        """ We list all the threads involving the user """
        check_notifications = self.request.GET.get("check_notifications", True)
        messages = Message.managers.get_lasts_messages_of_threads(self.request.rest_messaging_participant.id, check_who_read=True, check_is_notification=check_notifications)
        return messages

    @action(detail=True, methods=['post'], permission_classes=[IsInThread], serializer_class=SimpleMessageSerializer)
    def post_message(self, request, pk=None):
        """ Pk is the pk of the Thread to which the message belongs. """
        # we get the thread and check for permission
        thread = Thread.objects.get(id=pk)
        self.check_object_permissions(request, thread)
        # we get the body
        body = compat_get_request_data(self.request).get('body')
        # we create the message
        # Message.objects.save() could return an Exception
        try:
            message = Message(sender=request.rest_messaging_participant, thread=thread, body=body)
            message.save()
            serializer = SimpleMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(status=status.HTTP_412_PRECONDITION_FAILED)

    @action(detail=True, methods=['get'], permission_classes=[IsInThread], serializer_class=ComplexMessageSerializer)
    def list_messages_in_thread(self, request, pk=None):
        """ Pk is the pk of the Thread to which the messages belong. """
        # we get the thread and check for permission
        thread = Thread.objects.get(id=pk)
        self.check_object_permissions(request, thread)
        messages = Message.managers.get_all_messages_in_thread(participant_id=request.rest_messaging_participant.id, thread_id=thread.id, check_who_read=True)
        page = self.paginate_queryset(messages)
        if page is not None:
            return compat_get_paginated_response(self, page)
        serializer = ComplexMessageSerializer(messages, many=True)
        return Response(serializer.data)


class NotificationCheckView(mixins.ListModelMixin, viewsets.GenericViewSet):

    serializer_class = MessageNotificationCheckSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=False, methods=['post'])
    def check(self, request, *args, **kwargs):
        # we get the NotificationCheck instance corresponding to the user or we create it

        try:
            nc = NotificationCheck.objects.get(participant=request.rest_messaging_participant)
            if nc:
                nc.date_check = now()
                nc.save()
            status_code = status.HTTP_200_OK

        except Exception:
            nc = NotificationCheck.objects.create(participant=request.rest_messaging_participant, date_check=now())
            status_code = status.HTTP_201_CREATED

        serializer = self.get_serializer(nc)
        return Response(serializer.data, status=status_code)


class ParticipantAuthenticationView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    View that simply return the participant id of the user as set by the middleware, if it exists.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        participant = Participant.objects.get(id=self.request.rest_messaging_participant.id)
        return Response({'id': participant.id})
