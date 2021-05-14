# -*- coding: utf-8 -*-

"""
    pyGtkHelpers.ui.widgets
    ~~~~~~~~~~~~~~~~~~~~~~~

    Miscellaneous additional custom widgets

    :copyright: 2005-2010 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

from gi.repository import Gtk
from pyGtkHelpers.utils import gsignal, cmp


class StringList(Gtk.Box):
    """An editable list of strings
    """

    gsignal('content-changed')

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.set_border_width(6)
        self.set_size_request(0, 150)

        self.store = Gtk.ListStore(str)
        self.view = Gtk.TreeView()
        self.view.set_headers_visible(False)
        self.view.set_model(self.store)
        # XXX: scrollable?
        self.pack_start(self.view, expand=True, fill=True, padding=0)

        self.tv_col = Gtk.TreeViewColumn()
        self.text_renderer = Gtk.CellRendererText()
        self.tv_col.pack_start(self.text_renderer, expand=False)
        self.tv_col.add_attribute(self.text_renderer, 'text', 0)

        self.view.append_column(self.tv_col)

        selection = self.view.get_selection()
        selection.connect('changed', self._on_selection_changed)

        hb = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.value_entry = Gtk.Entry()
        self.value_entry.connect('changed', self._on_value_changed)
        self.value_entry.set_sensitive(False)
        self.pack_start(self.value_entry, expand=False, fill=False, padding=0)
        self.add_button = Gtk.Button.new_from_stock(Gtk.STOCK_NEW)
        self.add_button.connect('clicked', self._on_add)
        hb.pack_start(self.add_button, expand=False, fill=False, padding=0)
        self.rem_button = Gtk.Button.new_from_stock(Gtk.STOCK_REMOVE)
        self.rem_button.connect('clicked', self._on_rem)
        self.rem_button.set_sensitive(False)
        hb.pack_start(self.rem_button, expand=False, fill=False, padding=0)
        self.pack_start(hb, expand=False, fill=False, padding=0)
        self._current = None
        self._block = False

    def _on_add(self, button):
        itr = self.store.append(["New Item"])
        self.view.get_selection().select_iter(itr)
        self._emit_changed()

    def _on_rem(self, button):
        if self._current:
            self.store.remove(self._current)
            self._current = None
            self.view.get_selection().unselect_all()
        self._emit_changed()

    def _on_selection_changed(self, selection):
        model, itr = selection.get_selected()

        self.rem_button.set_sensitive(itr is not None)
        self._current = itr
        if itr is not None:
            self.value_entry.set_sensitive(True)
            self.value_entry.set_text(model[itr][0])
        else:
            self.value_entry.set_sensitive(False)
            self.value_entry.set_text('')

    def _on_value_changed(self, entry):
        if self._current is not None:
            self._block = True
            self.store.set(self._current, 0, entry.get_text())
            self._emit_changed()

    def _emit_changed(self):
        self.emit('content-changed')

    def update(self, value):
        if not self._block:
            self.store.clear()
            for item in value:
                self.store.append([item])
        self._block = False

    def read(self):
        return [i[0] for i in self.store]

    value = property(read, update)


class SimpleComboBox(Gtk.ComboBox):
    """A simple combobox that maps descriptions to keys
    """
    __gtype_name__ = 'PyGTKHelpersSimpleComboBox'

    def __init__(self, choices=None, default=None):
        Gtk.ComboBox.__init__(self)
        if choices and default is None:
            raise ValueError('default choice necessary')
        self.store = Gtk.ListStore(str, object)
        self.set_model(self.store)
        if choices is not None:
            self.set_choices(choices, default)

        self.renderer = Gtk.CellRendererText()
        self.pack_start(self.renderer, True)
        self.add_attribute(self.renderer, 'text', 0)

    def set_choices(self, choices, default):
        self.store.clear()
        for item in choices:
            itr = self.store.append((item[1], item[0]))
            if item[0] == default:
                self.set_active_iter(itr)


class AttrSortCombo(Gtk.Box):
    """
    A evil utility class that hijacks a object_list and forces ordering onto its
    model.
    """
    def __init__(self, object_list, attribute_list, default):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.set_border_width(3)
        from pyGtkHelpers.ui.widgets import SimpleComboBox
        from pyGtkHelpers.proxy import GtkComboBoxProxy

        self._object_list = object_list

        self._combo = SimpleComboBox(attribute_list, default)
        self._proxy = GtkComboBoxProxy(self._combo)
        self._proxy.connect_widget()
        self._proxy.connect('changed', self._on_configuration_changed)
        self._order_button = Gtk.ToggleToolButton(
            icon_name=Gtk.STOCK_SORT_DESCENDING)
        self._order_button.connect('toggled', self._on_configuration_changed)
        self._label = Gtk.Label(label='Sort')
        self.pack_start(self._label, expand=False, fill=False, padding=0)
        self.pack_start(self._combo, expand=False, fill=False, padding=0)
        self.pack_start(self._order_button, expand=False, fill=False, padding=0)
        self._on_configuration_changed()
        self.show_all()

    def _on_configuration_changed(self, *k):
        order_descending = self._order_button.get_active()
        if order_descending:
            order = Gtk.SortType.DESCENDING
        else:
            order = Gtk.SortType.ASCENDING
        attribute = self._proxy.read()

        try:
            self._object_list.sort_by(attribute, order)
        except AttributeError:
            model = self._object_list.get_model()
            model.set_default_sort_func(_attr_sort_func, attribute)
            model.set_sort_column_id(-1, order)


def _attr_sort_func(model, iter1, iter2, attribute):
    """Internal helper
    """
    attr1 = getattr(model[iter1][0], attribute, None)
    attr2 = getattr(model[iter2][0], attribute, None)
    return cmp(attr1, attr2)
