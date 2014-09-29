# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from django.core.exceptions import ImproperlyConfigured
from domains.utils import _thread_locals
from domains.compat import text_type


class HookBase(object):
    attribute = None

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        if self.attribute is None:
            raise ImproperlyConfigured("Please specify `attribute` into "
                                       "your hook class")

    def __repr__(self):
        return text_type(self.get())

    def __hash__(self):
        return self.get()

    def coerce(self, v):
        return v

    def get(self):
        return self.coerce(getattr(_thread_locals, self.attribute))

    def set(self, value):
        setattr(_thread_locals, self.attribute, self.coerce(value))

    def value(self, request):
        raise NotImplementedError()

    def apply(self, request):
        self.set(self.value(request))


class IntHookBase(HookBase, int):
    def coerce(self, v):
        return int(v)

    def __int__(self):
        try:
            return self.get()
        except AttributeError:
            self.set(1)
            return self.get()


class StrHookBase(HookBase, text_type):
    default_value = ''

    def coerce(self, v):
        return text_type(v)

    def __str__(self):
        try:
            return self.get()
        except AttributeError:
            self.set(self.default_value)
            return self.get()

    __unicode__ = __str__


class TupleHookBase(HookBase, tuple):
    default_value = ('default', )

    def coerce(self, v):
        return tuple(v)


class ListHookBase(HookBase, list):
    default_value = ['default']

    def coerce(self, v):
        return list(v)


class DictHookBase(HookBase, dict):
    default_value = {'default': 1}

    def coerce(self, v):
        return dict(v)


