# -*- coding: utf-8 -*-

"""
    pyGtkHelpers.ui.list_select
    ~~~~~~~~~~~~~~~

    List select.

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

from gi.repository import Gtk
from pyGtkHelpers.delegates import WindowView, SlaveView
from pyGtkHelpers.ui.objectlist import ObjectList, Column
from pyGtkHelpers.utils import gsignal
from pyGtkHelpers.ui.dict_as_attr_proxy import DictAsAttrProxy


class ListSelectView(SlaveView):
    """
    ListSelectView for selecting an item from a list.
    """
    gsignal('selection-changed', object)

    def __init__(self, items, column_name='name'):
        self.column_name = column_name
        self.items = items
        super(SlaveView, self).__init__()
        # self.create_ui()

    def create_ui(self):
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        columns = [Column(attr=self.column_name, sortable=True, editable=False,
                          resizeable=True)]
        self.list_box = ObjectList(columns)
        for item in self.items:
            self.add_item(item)

        s = self.list_box.get_selection()
        s.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.list_box.show_all()
        self.widget.pack_start(self.list_box)

    def add_item(self, item):
        item_object = DictAsAttrProxy({self.column_name: str(item)})
        self.list_box.append(item_object)

    def selected_items(self):
        return [i.as_dict.values()[0]
                for i in self.list_box.selected_items]

    def on_list_box__selection_changed(self, *args, **kwargs):
        self.emit('selection-changed', self.selected_items())


class TestWindow(WindowView):
    def create_ui(self):
        self.list_box = self.add_slave(ListSelectView(['hello', 'world']).create_ui(), 'widget')

    def on_list_box__selection_changed(self, list_box, selected_items):
        print(selected_items)


if __name__ == '__main__':
    window_view = TestWindow()
    window_view.show_and_run()
