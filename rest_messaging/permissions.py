# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from rest_framework import permissions


class IsInThread(permissions.BasePermission):
    """
    Custom permission to only allow participants to a thread to access it.
    """
    def has_object_permission(self, request, view, obj):
        """ Here we ensure the user is in the thread. """
        return obj.is_participant(request)

    def has_permission(self, request, view):
        """ We always required a logged in user. """
        if request.user.is_authenticated:
            return True
        return False
