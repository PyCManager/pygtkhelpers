# -*- coding: utf-8 -*-
"""
    pyGtkHelpers.utils.formatter
    ~~~~~~~~~~~~

    Helper library for PyGTK

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL2 or later
"""

import string
from html import escape as _xml_escape


class XFormatter(string.Formatter):
    """
    extended string formatter supporting xml entity escape
    """
    def __init__(self, *lookup_objects, **extra_converters):
        # add e as xml escape converter if the name is not used
        if 'e' not in extra_converters:
            extra_converters['e'] = _xml_escape
        self.extra_converters = extra_converters
        self.lookup_objects = lookup_objects

    def get_value(self, key, args, kwargs):
        try:
            return super(XFormatter, self).get_value(key, args, kwargs)
        except LookupError:
            if isinstance(key, (str, bytes)):
                for obj in self.lookup_objects:
                    if hasattr(obj, key):
                        return getattr(obj, key)
            raise  # reraise the lookup error

    def convert_field(self, value, conversion):
        if conversion in self.extra_converters:
            return self.extra_converters[conversion](value)
        return super(XFormatter, self).convert_field(value, conversion)

    def format_field(self, value, conversion):
        if conversion in self.extra_converters:
            return self.extra_converters[conversion](value)
        return super(XFormatter, self).format_field(value, conversion)


def eformat(form, *k, **kw):
    """
    :param Format form:
    :param k:
    :param kw:
    :return:
    """
    return XFormatter().vformat(form, k, kw)


class MarkupMixin(object):
    """
    adds a markup property based on eformat
    using self.format as format string
    and self=self as format args
    """
    format = None

    markup_converters = {}

    def markup_kwargs(self):
        return {}

    @property
    def markup(self):
        formatter = XFormatter(self, **self.markup_converters)
        return formatter.vformat(self.format, (), self.markup_kwargs())
