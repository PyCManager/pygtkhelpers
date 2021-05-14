# -*- coding: utf-8 -*-
"""
    pyGtkHelpers.utils.gsignal
    ~~~~~~~~~~~~

    Helper library for PyGTK

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL2 or later
"""

import struct
import sys

from gi.repository import GObject


def gsignal(name, *args, **kwargs):
    """Add a GObject signal to the current object.

    It current supports the following types:
        - str, int, float, long, object, enum

    :param name: name of the signal
    :param args: types for signal parameters,
        if the first one is a string 'override', the signal will be
        overridden and must therefor exists in the parent GObject.

    .. note:: flags: A combination of;

      - GObject.SignalFlags.RUN_FIRST
      - GObject.SignalFlags.RUN_LAST
      - GObject.SignalFlags.RUN_CLEANUP
      - GObject.SignalFlags.NO_RECURSE
      - GObject.SignalFlags.DETAILED
      - GObject.SignalFlags.ACTION
      - GObject.SignalFlags.NO_HOOKS

    """

    frame = sys._getframe(1)
    try:
        locals = frame.f_locals
    finally:
        del frame

    dict_ = locals.setdefault('__gsignals__', {})

    if args and args[0] == 'override':
        dict_[name] = 'override'
    else:
        retval = kwargs.get('retval', None)
        if retval is None:
            default_flags = GObject.SignalFlags.RUN_FIRST
        else:
            default_flags = GObject.SignalFlags.RUN_LAST

        flags = kwargs.get('flags', default_flags)
        if retval is not None and flags != GObject.SignalFlags.RUN_LAST:
            raise TypeError(
                "You cannot use a return value without setting flags to "
                "GGObject.SignalFlags.RUN_LAST")

        dict_[name] = (flags, retval, args)


def _max(c):
    # Python 2.3 does not like bitshifting here
    return 2 ** ((8 * struct.calcsize(c)) - 1) - 1


_MAX_VALUES = {int: _max('i'),
               float: float(2**1024 - 2**971),
               'long': _max('l')}
_DEFAULT_VALUES = {str: '', float: 0.0, int: 0, 'long': 0}


def gproperty(name, ptype, default=None, nick='', blurb='',
              flags=GObject.PARAM_READWRITE, **kwargs):
    """Add a GObject property to the current object.

    :param name:   name of property
    :param ptype:   type of property
    :param default:  default value
    :param nick:     short description
    :param blurb:    long description
    :param flags:    parameter flags, a combination of:
      - GObject.PARAM_READABLE
      - GObject.PARAM_READWRITE
      - GObject.PARAM_WRITABLE
      - GObject.PARAM_CONSTRUCT
      - GObject.PARAM_CONSTRUCT_ONLY
      - GObject.PARAM_LAX_VALIDATION

    Optional, only for int, float, long types:

    :param minimum: minimum allowed value
    :param: maximum: maximum allowed value
    """

    # General type checking
    if default is None:
        default = _DEFAULT_VALUES.get(ptype)
    elif not isinstance(default, ptype):
        raise TypeError("default must be of type %s, not %r" % (
            ptype, default))
    if not isinstance(nick, str):
        raise TypeError('nick for property %s must be a string, not %r' % (
            name, nick))
    nick = nick or name
    if not isinstance(blurb, str):
        raise TypeError('blurb for property %s must be a string, not %r' % (
            name, blurb))

    # Specific type checking
    if ptype == int or ptype == float:
        default = (kwargs.get('minimum', ptype(0)),
                   kwargs.get('maximum', _MAX_VALUES[ptype]),
                   default)
    elif ptype == bool:
        if default is not True and default is not False:
            raise TypeError("default must be True or False, not %r" % default)
        default = default,
    elif GObject.type_is_a(ptype, GObject.GEnum):
        if default is None:
            raise TypeError("enum properties needs a default value")
        elif not isinstance(default, ptype):
            raise TypeError("enum value %s must be an instance of %r" % (default, ptype))
        default = default,
    elif ptype == str:
        default = default,
    elif ptype == object:
        if default is not None:
            raise TypeError("object types does not have default values")
        default = ()
    else:
        raise NotImplementedError("type %r" % ptype)

    if flags < 0 or flags > 32:
        raise TypeError("invalid flag value: %r" % (flags,))

    frame = sys._getframe(1)
    try:
        locals = frame.f_locals
        dict_ = locals.setdefault('__gproperties__', {})
    finally:
        del frame

    dict_[name] = (ptype, nick, blurb) + default + (flags,)
