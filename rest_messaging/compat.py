# coding=utf8
# -*- coding: utf8 -*-
# vim: set fileencoding=utf8 :

from __future__ import unicode_literals
from django.conf import settings
from rest_framework import VERSION, serializers
from rest_framework.response import Response
from rest_messaging.pagination import MessagePagination


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


def compat_get_paginated_response(view, page):
    """ get_paginated_response is unknown to DRF 3.0 """
    if DRFVLIST[0] == 3 and DRFVLIST[1] >= 1:
        from rest_messaging.serializers import ComplexMessageSerializer  # circular import
        serializer = ComplexMessageSerializer(page, many=True)
        return view.get_paginated_response(serializer.data)
    else:
        serializer = view.get_pagination_serializer(page)
        return Response(serializer.data)


def compat_pagination_messages(cls):
    """
    For DRF 3.1 and higher, pagination is defined at the paginator level (see http://www.django-rest-framework.org/topics/3.2-announcement/).
    For DRF 3.0 and lower, it can be handled at the view level.
    """
    if DRFVLIST[0] == 3 and DRFVLIST[1] >= 1:
        setattr(cls, "pagination_class", MessagePagination)
        return cls
    else:
        # DRF 2 pagination
        setattr(cls, "paginate_by", getattr(settings, "DJANGO_REST_MESSAGING_MESSAGES_PAGE_SIZE", 30))
        return cls
