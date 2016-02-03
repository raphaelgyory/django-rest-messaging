# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.apps import AppConfig


class MessagesAppConfig(AppConfig):

    name = 'rest_messaging'
    verbose_name = 'Messages App'

    def ready(self):
        # import signal handlers
        # from rest_messaging import signals
        pass  # we use no signal for now
