# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.conf.urls import include, url


urlpatterns = [
    url(r'^messaging/', include(('rest_messaging.urls', 'rest_messaging'), namespace='rest_messaging')),
]
