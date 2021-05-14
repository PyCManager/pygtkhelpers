# -*- coding: utf-8 -*-
"""
    pyGtkHelpers.utils.functions
    ~~~~~~~~~~~~~~~~~~

    Utilities for handling some of the wonders of PyGTK.
    gproperty and gsignal are mostly taken from kiwi.utils

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""


def dict_to_form(dict_):
    """
    Generate a flatland form based on a pandas Series.
    """
    from flatland import Boolean, Form, String, Integer, Float

    def is_float(v):
        try:
            return (float(str(v)), True)[1]
        except (ValueError, TypeError):
            return False

    def is_int(v):
        try:
            return (int(str(v)), True)[1]
        except (ValueError, TypeError):
            return False

    def is_bool(v):
        return v in (True, False)

    schema_entries = []
    for k, v in dict_.iteritems():
        if is_int(v):
            schema_entries.append(Integer.named(k).using(default=v,
                                                         optional=True))
        elif is_float(v):
            schema_entries.append(Float.named(k).using(default=v,
                                                       optional=True))
        elif is_bool(v):
            schema_entries.append(Boolean.named(k).using(default=v,
                                                         optional=True))
        elif type(v) == str:
            schema_entries.append(String.named(k).using(default=v,
                                                        optional=True))

    return Form.of(*schema_entries)


def cmp(a, b):
    return (a > b) - (a < b)
