"""
    pyGtkHelpers.ui.extra_dialogs
    ~~~~~~~~~~~~~~~

    Extra Components.

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

import os

from gi.repository import Gtk
from flatland.schema import String, Form, Integer
from flatland.validation import ValueAtLeast, ValueAtMost

from pyGtkHelpers.ui.form_view_dialog import FormViewDialog
from pyGtkHelpers.ui.dialogs import yesno as _yesno


class Defaults(object):
    def __init__(self):
        self._parent_widget = None

    @property
    def parent_widget(self):
        return self._parent_widget

    @parent_widget.setter
    def parent_widget(self, parent):
        self._parent_widget = parent


DEFAULTS = Defaults()


def combobox_set_model_from_list(cb, items):
    """Setup a ComboBox or ComboBoxEntry based on a list of strings."""
    cb.clear()
    model = Gtk.ListStore(str)
    for i in items:
        model.append([i])
    cb.set_model(model)
    if type(cb) == Gtk.ComboBoxEntry:
        cb.set_text_column(0)
    elif type(cb) == Gtk.ComboBox:
        cell = Gtk.CellRendererText()
        cb.pack_start(cell, True)
        cb.add_attribute(cell, 'text', 0)


def combobox_get_active_text(cb):
    model = cb.get_model()
    active = cb.get_active()
    if active < 0:
        return None
    return model[active][0]


def textview_get_text(textview):
    buffer_ = textview.get_buffer()
    start = buffer_.get_start_iter()
    end = buffer_.get_end_iter()
    return buffer_.get_text(start, end)


def field_entry_dialog(field, value=None, title='Input value', parent=None,
                       use_markup=True):
    if parent is None:
        parent = DEFAULTS.parent_widget
    form = Form.of(field)
    dialog = FormViewDialog(form, title=title, parent=parent)
    if value is not None:
        values = {field.name: value}
    else:
        values = None
    valid, response = dialog.run(values, use_markup=use_markup)
    return valid, response.values()[0]


def integer_entry_dialog(name, value=0, title='Input value', min_value=None,
                         max_value=None, parent=None, use_markup=True):
    if parent is None:
        parent = DEFAULTS.parent_widget
    validators = []
    if min_value is not None:
        ValueAtLeast(minimum=min_value)
    if max_value is not None:
        ValueAtMost(maximum=max_value)

    valid, response = field_entry_dialog(
        Integer.named(name).using(validators=validators),
        value,
        title,
        parent=parent,
        use_markup=use_markup
    )
    if valid:
        return response
    return None


def text_entry_dialog(name, value='', title='Input value', parent=None,
                      use_markup=True):
    valid, response = field_entry_dialog(String.named(name), value, title,
                                         parent=parent, use_markup=use_markup)
    if parent is None:
        parent = DEFAULTS.parent_widget
    if valid:
        return response
    return None


if os.name == 'nt':
    def yesno(*args, **kwargs):
        parent = kwargs.get('parent', None)
        if parent is None:
            parent = DEFAULTS.parent_widget
        return _yesno(
            *args,
            parent=parent,
            alt_button_order=(
                Gtk.ResponseType.YES,
                Gtk.ResponseType.NO
            ),
            **kwargs
        )
else:
    def yesno(*args, **kwargs):
        parent = kwargs.get('parent', None)
        if parent is None:
            parent = DEFAULTS.parent_widget
        return _yesno(*args, parent=parent, **kwargs)
