# -*- coding: utf-8 -*-
"""
    pyGtkHelpers.utils.ui
    ~~~~~~~~~~~~~~~~~~

    Utilities for handling some of the wonders of PyGTK.
    gproperty and gsignal are mostly taken from kiwi.utils

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

import time

from gi.repository import Gtk, GObject


def refresh_gui(delay=0.0001, wait=0.0001):
    """Use up all the events waiting to be run

    :param delay: Time to wait before using events
    :param wait: Time to wait between iterations of events

    This function will block until all pending events are emitted. This is
    useful in testing to ensure signals and other asynchronous functionality
    is required to take place.
    """
    time.sleep(delay)
    while Gtk.events_pending():
        Gtk.main_iteration_do(blocking=False)
        time.sleep(wait)


def _get_in_window(widget):
    from pyGtkHelpers.delegates import BaseDelegate
    if isinstance(widget, Gtk.Window):
        return widget
    elif isinstance(widget, BaseDelegate):
        return _get_in_window(widget.widget)
    else:
        w = Gtk.Window()
        w.add(widget)
        return w


def run_in_window(target, on_destroy=Gtk.main_quit):
    """Run a widget, or a delegate in a Window
    """
    w = _get_in_window(target)
    if on_destroy:
        w.connect('destroy', on_destroy)
    w.resize(500, 400)
    w.move(100, 100)
    w.show_all()
    Gtk.main()
