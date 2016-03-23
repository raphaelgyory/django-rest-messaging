# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.conf.urls import include, url
from rest_framework import routers
from rest_messaging import views


# Create a router and register our viewsets with it.
router = routers.SimpleRouter()
router.register(r'threads', views.ThreadView, 'threads')
router.register(r'messages', views.MessageView, 'messages')
router.register(r'notifications', views.NotificationCheckView, 'notifications')
router.register(r'authentication', views.ParticipantAuthenticationView, 'authentication')

# API endpoints, determined automatically by the router.
urlpatterns = [
    url(r'^', include(router.urls)),
]
