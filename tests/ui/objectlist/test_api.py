import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.utils import refresh_gui
from .conftest import (
    User,
    items,
    user,
    user2,
    user3
)

from pyGtkHelpers.test import CheckCalled


class TestApi(unittest.TestCase):
    def test_append(self):
        self.assertEqual(len(items), 0)
        items.append(user)
        self.assertEqual(len(items), 1)
        self.assertIs(items[0], user)
        self.assertIn(user, items)

        self.assertNotIn(User(name="hans", age=10), items)

        self.assertRaises(ValueError, items.append, user)

    def test_append_selected(self):
        items.append(user, select=True)

        assert items.selected_item is user

    def test_append_unselected(self):
        items.append(user, select=False)
        self.assertIsNone(items.selected_item)

    def test_select_single_fails_when_select_multiple_is_set(self):
        items.append(user)
        items.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        self.assertRaises(AttributeError, 'items.selected_item = user')
        self.assertRaises(AttributeError, 'items.selected_item')
        items.selected_items = [user]
        refresh_gui()
        self.assertEqual(items.selected_items, [user])

    def test_extend(self):
        items.extend([
            User('hans', 22),
            User('peter', 22),
            ])
        self.assertEqual(len(items), 2)

    def test_remove(self):
        items.append(user)
        self.assertIn(user, items)
        items.remove(user)
        self.assertNotIn(user, items)

    def test_deselect(self):
        items.append(user)
        items.selected_item = user
        refresh_gui()
        items.selected_item = None
        refresh_gui()

    def test_deselect_multiple(self):
        listing = [user, user2]
        items.extend(listing)
        items.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)
        items.selected_items = listing
        refresh_gui()
        self.assertEqual(items.selected_items, listing)
        items.selected_items = []
        refresh_gui()
        self.assertEqual(items.selected_items, [])

        items.selected_items = listing
        refresh_gui()
        self.assertEqual(items.selected_items, listing)
        items.selected_items = None
        refresh_gui()
        self.assertEqual(items.selected_items, [])

    def test_remove_missing(self):
        self.assertRaises(ValueError.remove, user)

    def test_selection_changed_signal(self):
        items.append(user)
        selection_changed = CheckCalled(items, 'selection-changed')
        items.selected_item = user
        self.assertTrue(selection_changed.called)

    def test_move_item_up(self):
        items.append(user)
        items.append(user2)
        items.move_item_up(user2)
        self.assertIs(items._object_at_iter(0), user2)
        self.assertIs(items._object_at_iter(1), user)

    def test_move_item_down(self):
        items.append(user)
        items.append(user2)
        items.move_item_down(user)
        self.assertIs(items._object_at_iter(0), user2)
        self.assertIs(items._object_at_iter(1), user)

    def test_move_first_item_up(self):
        items.append(user)
        items.append(user2)
        items.move_item_up(user)
        self.assertIs(items._object_at_iter(0), user)
        self.assertIs(items._object_at_iter(1), user2)

    def test_move_last_item_down(self):
        items.append(user)
        items.append(user2)
        items.move_item_down(user2)
        self.assertIs(items._object_at_iter(0), user)
        self.assertIs(items._object_at_iter(1), user2)

    def test_move_subitem_down(self):
        items.append(user)
        items.append(user2, parent=user)
        items.append(user3, parent=user)
        items.move_item_down(user2)
        self.assertEqual(
            items._path_for(user2),
            items._path_for_iter(items._next_iter_for(user3))
        )

    def test_move_last_subitem_down(self):
        items.append(user)
        items.append(user2, parent=user)
        items.append(user3, parent=user)
        items.move_item_down(user3)
        self.assertEqual(
            items._path_for(user3),
            items._path_for_iter(items._next_iter_for(user2))
        )

    def test_move_subitem_up(self):
        items.append(user)
        items.append(user2, parent=user)
        items.append(user3, parent=user)
        items.move_item_up(user3)
        self.assertEqual(
            items._path_for(user2),
            items._path_for_iter(items._next_iter_for(user3))
        )

    def test_move_last_subitem_up(self):
        items.append(user)
        items.append(user2, parent=user)
        items.append(user3, parent=user)
        items.move_item_up(user2)
        self.assertEqual(
            items._path_for(user3),
            items._path_for_iter(items._next_iter_for(user2))
        )

    def test_view_iters(self):
        items.extend([user, user2, user3])
        items.set_visible_func(lambda obj: obj.age < 100)
        refresh_gui()
        self.assertTrue(items.item_visible(user))
        self.assertFalse(items.item_visible(user3))

    def test_item_after(self):
        items.extend([user, user2, user3])
        self.assertIs(items.item_after(user), user2)
        self.assertIs(items.item_after(user2), user3)
        self.assertIsNone(items.item_after(user3))

    def test_item_before(self):
        items.extend([user, user2, user3])
        self.assertIs(items.item_before(user2), user)
        self.assertIs(items.item_before(user3), user2)
        self.assertIsNone(items.item_before(user))


if __name__ == '__main__':
    unittest.main()
