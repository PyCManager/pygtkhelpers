import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.ui.objectlist import ObjectList, Column
from pyGtkHelpers.utils import refresh_gui
from pyGtkHelpers.test import CheckCalled
from unittest.mock import Mock


def _sort_key(obj):
    # key on the last letter of the name
    return obj.name[-1]


class TestSort(unittest.TestCase):

    def test_sort_by_attr_default(self, items):
        items.sort_by('name')
        assert items.model_sort.has_default_sort_func()

    def test_sort_by_attr_asc(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        assert items[0] is user
        assert items[1] is user2
        assert items[2] is user3
        items.sort_by('name')
        it = [i[0] for i in items.model_sort]
        assert it[0] is user2
        assert it[1] is user
        assert it[2] is user3

    def test_sort_by_attr_desc(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        assert items[0] is user
        assert items[1] is user2
        assert items[2] is user3
        items.sort_by('name', direction='desc')
        it = [i[0] for i in items.model_sort]
        assert it[0] is user3
        assert it[1] is user
        assert it[2] is user2

    def test_sort_by_key_asc(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        assert items[0] is user
        assert items[1] is user2
        assert items[2] is user3
        items.sort_by(_sort_key)
        it = [i[0] for i in items.model_sort]
        assert it[0] is user3
        assert it[1] is user2
        assert it[2] is user

    def test_sort_by_key_desc(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        assert items[0] is user
        assert items[1] is user2
        assert items[2] is user3
        items.sort_by(_sort_key, '-')
        it = [i[0] for i in items.model_sort]
        assert it[0] is user
        assert it[1] is user2
        assert it[2] is user3

    def test_sort_by_col(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        assert items[0] is user
        assert items[1] is user2
        assert items[2] is user3
        # simulate a click on the header
        items.model_sort.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        it = [i[0] for i in items.model_sort]
        assert it[0] is user2
        assert it[1] is user
        assert it[2] is user3

    def test_sort_by_col_desc(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        it = [i[0] for i in items.model_sort]
        assert it[0] is user
        assert it[1] is user2
        assert it[2] is user3
        ui = items._sort_iter_for(user)
        print(items.model_sort.iter_next(ui))
        # simulate a click on the header
        items.model_sort.set_sort_column_id(0, Gtk.SortType.DESCENDING)
        it = [i[0] for i in items.model_sort]
        assert it[0] is user3
        assert it[1] is user
        assert it[2] is user2

    def test_sort_item_activated(self, items, user, user2, user3):
        items.extend([user, user2, user3])
        mock = Mock()
        items.connect('item-activated', mock.cb)
        items.emit('row-activated', '0', Gtk.TreeViewColumn())
        assert mock.cb.call_args[0][1] is user

        items.sort_by('age', '-')
        items.emit('row-activated', '0', Gtk.TreeViewColumn())
        assert mock.cb.call_args[0][1] is user3


if __name__ == '__main__':
    unittest.main()
