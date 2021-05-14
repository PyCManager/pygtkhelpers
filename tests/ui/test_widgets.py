import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.ui.widgets import StringList, AttrSortCombo
from pyGtkHelpers.ui.objectlist import ObjectList
from unittest.mock import Mock


pl = StringList()


class TestWidgets(unittest.TestCase):

    def test_proxy_stringlist_create(self):
        self.assertFalse(pl.view.get_headers_visible())

    def test_sl_set_value(self):
        pl.value = ['a', 'b']
        self.assertEqual(pl.value, ['a', 'b'])

    def test_sl_add_button(self):
        assert len(pl.value) == 0
        pl.add_button.clicked()
        self.assertEqual(pl.value, ['New Item'])

    def test_sl_add_selects(self):
        pl.add_button.clicked()
        text = pl.value_entry.get_text()
        self.assertEqual(text, 'New Item')
        self.assertTrue(pl.value_entry.props.editable)

    def test_pl_remove_desensible(self):
        pl.add_button.clicked()
        pl.rem_button.clicked()
        self.assertEqual(pl.value, [])

        self.assertFalse(pl.value_entry.props.sensitive)
        self.assertEqual(pl.value_entry.get_text(), '')
        pl.add_button.clicked()

        self.assertTrue(pl.value_entry.props.sensitive)

    def test_pl_edit(self):
        pl.add_button.clicked()
        pl.value_entry.set_text('test')
        self.assertEqual(pl.value, ['test'])

    def test_attrsortcombo_with_treeview(self):

        ol = Mock(spec=Gtk.TreeView)
        model = ol.get_model.return_value = Mock(spec=Gtk.TreeSortable)

        sort = AttrSortCombo(ol, [
            ('name', 'Der name'),
            ('age', 'Das Alter'),
            ], 'name')

        sort_func = model.set_default_sort_func
        (func, name), kw = sort_func.call_args
        self.assertEqual(name, 'Der name')

        sort._proxy.update('age')
        (func, name), kw = sort_func.call_args
        self.assertEqual(name, 'Der name')

        # the combo is connected
        sort._combo.set_active(0)
        (func, name), kw = sort_func.call_args
        self.assertEqual(name, 'Der name')

        col = model.set_sort_column_id
        self.assertEqual(col.call_args[0], (-1, Gtk.SortType.ASCENDING))

        sort._order_button.set_active(True)
        self.assertEqual(col.call_args[0], (-1, Gtk.SortType.DESCENDING))

    def test_attrsortcombo_with_objectlist(self):

        ol = Mock(spec=ObjectList)

        sort = AttrSortCombo(ol, [
            ('name', 'Der name'),
            ('age', 'Das Alter'),
            ], 'name')

        (name, order), kw = ol.sort_by.call_args
        self.assertEqual(name, 'Der name')

        sort._proxy.update('age')
        name, order = ol.sort_by.call_args[0]
        print(name, order)
        self.assertEqual(name, 'Der name')

        # the combo is connected
        sort._combo.set_active(0)
        name, order = ol.sort_by.call_args[0]
        self.assertEqual(order, Gtk.SortType.ASCENDING)

        sort._order_button.set_active(True)
        name, order = ol.sort_by.call_args[0]
        self.assertEqual(order, Gtk.SortType.DESCENDING)


if __name__ == '__main__':
    unittest.main()
