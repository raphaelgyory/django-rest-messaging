# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from rest_framework import VERSION
from rest_framework import serializers


DRFVLIST = [int(x) for x in VERSION.split(".")]


def compat_serializer_method_field(method_name=None):
    """ method_name changed in DRF > 3. See http://www.django-rest-framework.org/topics/3.0-announcement/#optional-argument-to-serializermethodfield. """
    if DRFVLIST[0] >= 3:
        return serializers.SerializerMethodField()
    else:
        return serializers.SerializerMethodField(method_name=method_name)


def compat_serializer_check_is_valid(serializer):
    """ http://www.django-rest-framework.org/topics/3.0-announcement/#using-is_validraise_exceptiontrue """
    if DRFVLIST[0] >= 3:
        serializer.is_valid(raise_exception=True)
    else:
        if not serializer.is_valid():
            serializers.ValidationError('The serializer raises a validation error')


def compat_thread_serializer_set():
    """ We create the Thread manually and must assign it to the serializer. DRF 3 uses serializer.instance while DRF 2 uses serializer.object """
    if DRFVLIST[0] >= 3:
        return "instance"
    else:
        return "object"


def compat_serializer_attr(serializer, obj):
    """
    Required only for DRF 3.1, which does not make dynamically added attribute available in obj in serializer.
    This is a quick solution but works without breajing anything.
    """
    if DRFVLIST[0] == 3 and DRFVLIST[1] == 1:
        for i in serializer.instance:
            if i.id == obj.id:
                return i
    else:
        return obj


def compat_get_request_data(request):
    """ http://www.django-rest-framework.org/topics/3.0-announcement/#request-objects """
    if DRFVLIST[0] >= 3:
        return request.data
    else:
        return request.DATA


def compat_perform_update(instance, serializer):
    """ Verbatim copy of compat_perform_update mixin for DRF 2.4 compatibility. """
    if DRFVLIST[0] == 2:
        serializer.save()
