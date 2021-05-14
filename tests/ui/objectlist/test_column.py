import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.utils import refresh_gui
from pyGtkHelpers.ui.objectlist import Column


class TestColumn(unittest.TestCase):

    def test_column_title(self):
        col = Column("name")
        view_col = col.create_treecolumn(None)
        self.assertEqual(view_col.get_title(), "Name")

        title_col = Column(title="Test", cells=[])
        title_view_col = title_col.create_treecolumn(None)
        self.assertEqual(title_view_col.get_title(), 'Test')
        self.assertEqual(len(title_view_col.get_cells()), 0)

    def test_column_visiblility(self):
        col = Column('test')
        view_col = col.create_treecolumn(None)
        self.assertTrue(view_col.get_visible())

    def test_column_invisiblility(self):
        col = Column('test', visible=False)
        view_col = col.create_treecolumn(None)
        self.assertFalse(view_col.get_visible())

    def test_column_width(self):
        col = Column('test', width=30)
        view_col = col.create_treecolumn(None)
        refresh_gui()
        self.assertEqual(view_col.get_sizing(), Gtk.TreeViewColumnSizing.FIXED)
        self.assertEqual(view_col.get_fixed_width(), 30)

    def test_column_expandable(self):
        col = Column('name', expand=True)
        tree_view_column = col.create_treecolumn(None)
        self.assertTrue(tree_view_column.props.expand)


if __name__ == '__main__':
    unittest.main()
