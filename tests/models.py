# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Profile(models.Model):
    """
    This test-only model is for showing how ThreadSerializer can get access to data about the users, beyond their simple ids.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.TextField()  # just for the example; ImageField would have been better but obliges us to install Pillow, which is quite a hassle just to test the custom serializer
    contact = models.TextField()

    def __str__(self):
        return self.user.username
