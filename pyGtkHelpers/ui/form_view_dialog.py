# -*- coding: utf-8 -*-

"""
    pyGtkHelpers.ui.form_view_dialog
    ~~~~~~~~~~~~~~~

    From View Dialog.

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

import pkgutil

from gi.repository import Gtk
from collections import OrderedDict
from pyGtkHelpers.forms import FormView


def create_form_view(form, values=None, use_markup=True):
    FormView.schema_type = form
    form_view = FormView()
    for field_i in form_view.form.schema.field_schema:
        name_i = field_i.name
        form_field_i = form_view.form.fields[name_i]
        if values and name_i in values:
            value = values[name_i]
        else:
            value = form_field_i.element.default_value
        if not form_field_i.element.set(value):
            raise ValueError('"%s" is not a valid value for field "%s"' %
                             (value, name_i))
        form_field_i.proxy.set_widget_value(value)
        if hasattr(form_field_i.widget, 'set_activates_default'):
            form_field_i.widget.set_activates_default(Gtk.true())
        form_field_i.label_widget.set_use_markup(use_markup)
    return form_view


class FormViewDialog(object):
    default_parent = None

    def __init__(self, form_class, title=None, short_desc=None, long_desc=None,
                 parent=None):
        """
        Parameters
        ----------
        title : str, optional
            The short description
        short_desc : str, optional
            The short description
        long_desc : str, optional
            The long description
        parent : Gtk.Window, optional
            The parent window to make this dialog transient to
        """
        self.title = title
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.parent = parent
        self.form_class = form_class

    def create_ui(self):
        """
        .. versionchanged:: 0.21.2
            Load the builder configuration file using :func:`pkgutil.getdata`,
            which supports loading from `.zip` archives (e.g., in an app
            packaged with Py2Exe).
        """
        builder = Gtk.Builder()
        # Read glade file using `pkgutil` to also support loading from `.zip`
        # files (e.g., in app packaged with Py2Exe).
        glade_str = pkgutil.get_data(__name__,
                                     'glade/form_view_dialog.glade')
        builder.add_from_string(glade_str)

        self.window = builder.get_object('form_view_dialog')
        self.vbox_form = builder.get_object('vbox_form')
        if self.title:
            self.window.set_title(self.title)
        if self.short_desc:
            self.short_label = Gtk.Label()
            self.short_label.set_text(self.short_desc)
            self.short_label.set_alignment(0, .5)
            self.vbox_form.pack_start(self.short_label, expand=True, fill=True)
        if self.long_desc:
            self.long_label = Gtk.Label()
            self.long_label.set_text(self.long_desc)
            self.long_label.set_alignment(.1, .5)
            self.long_expander = Gtk.Expander(label='Details')
            self.long_expander.set_spacing(5)
            self.long_expander.add(self.long_label)
            self.vbox_form.pack_start(self.long_expander, expand=True,
                                      fill=True)
        if self.parent is None:
            self.parent = self.default_parent
        self.window.set_default_response(Gtk.ResponseType.OK)
        self.window.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        if self.parent:
            self.window.set_transient_for(self.parent)
        self.window.show_all()

    def create_form_view(self, values=None, use_markup=True):
        self.form_view = create_form_view(self.form_class, values=values,
                                          use_markup=use_markup)

    def run(self, values=None, parent=None, use_markup=True):
        self.create_ui()
        self.create_form_view(values=values, use_markup=use_markup)
        self.form_view.connect('changed', self.on_changed)
        self.form_view.widget.show_all()
        self.vbox_form.pack_start(self.form_view.widget)
        response = self.window.run()
        self.window.destroy()
        return ((response == 0),
                OrderedDict([(name, f.element.value)
                             for name, f in
                             self.form_view.form.fields.items()]))

    def on_changed(self, form_view, proxy_group, proxy, field_name, new_value):
        pass
