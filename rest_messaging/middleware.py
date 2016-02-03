# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.core.cache import cache
from rest_messaging.models import Participant


class MessagingMiddleware(object):
    """
    Ensures we can access request.user as request.rest_messaging_participant in every request.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):

        assert hasattr(request, 'user'), (
            "The django-rest-messaging MessagingMiddleware requires an authentication middleware "
            "to be installed because request.user must be available."
        )

        if request.user.is_authenticated():

            participant = cache.get('rest_messaging_participant_{0}'.format(request.user.id), None)

            if participant is None:
                # either we create the participant or we retrieve him
                try:
                    participant = Participant.objects.get(id=request.user.id)
                except:
                    participant = Participant.objects.create(id=request.user.id)
                cache.set('rest_messaging_participant_{0}'.format(request.user.id), participant, 60 * 60)  # cached for 60 minutes
        else:
            participant = None

        request.rest_messaging_participant = participant

        return None
