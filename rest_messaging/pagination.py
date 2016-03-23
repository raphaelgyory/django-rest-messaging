# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.conf import settings

try:
    from rest_framework.pagination import PageNumberPagination
except:
    PageNumberPagination = object  # dummy import


class MessagePagination(PageNumberPagination):
    page_size = getattr(settings, "DJANGO_REST_MESSAGING_MESSAGES_PAGE_SIZE", 30)
