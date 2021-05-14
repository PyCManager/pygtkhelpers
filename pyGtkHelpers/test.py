# -*- coding: utf-8 -*-

"""
    pyGtkHelpers.test
    ~~~~~~~~~~~~~~~~~

    Assistance for unittesting pygtk

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""


class CheckCalled(object):
    """Utility to check whether a signal has been emitted

    :param obj: The Object that will fire the signal
    :param signal: The signal name

    This class should be used when testing whether a signal has been called.
    It could be used in conjuntion with :func:`pygtkhelpers.utils.refresh_gui`
    in order to block the UI adequately to check::

        >>> from gi.repository import Gtk
        >>> from pyGtkHelpers.utils import refresh_gui
        >>> b = Gtk.Button()
        >>> check = CheckCalled(b, 'clicked')
        >>> b.clicked()
        >>> assert check.called
        >>> assert check.called_count = 1
        >>> b.click()
        >>> assert check.called_count = 2

    """
    def __init__(self, obj, signal):
        self.called = None
        self.called_count = 0
        obj.connect(signal, self)

    def __call__(self, *k):
        self.called = k
        self.called_count += 1
