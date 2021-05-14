import unittest
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Pango', '1.0')

from gi.repository import GdkPixbuf, Pango
from unittest.mock import Mock
from pyGtkHelpers.ui.objectlist import Cell, Column


class TestCell(unittest.TestCase):

    def test_make_cells(self):
        col = Column(title='Test', cells=[
            Cell('name', int),
            Cell('name2', int),
            ])
        view_col = col.create_treecolumn(None)

        self.assertEqual(len(view_col.get_cells()), 2)

    def test_cell_format_func(self):
        cell = Cell('test', format_func=str)
        self.assertEqual(cell.format_data(1), '1')

    def test_cell_format_string(self):
        cell = Cell('test', format='hoo %s')
        self.assertEqual(cell.format_data(1), 'hoo 1')

    @unittest.expectedFailure
    def test_cell_format_for_obj(self):
        cell = Cell(None)
        renderer = Mock()
        cell.mappers[0](cell, 1, renderer)
        self.assertEqual(renderer.set_property.call_args[0][1], 1)

    def test_default_type(self):
        cell = Cell('test')
        self.assertEqual(cell.mappers[0].prop, 'text')

    def test_pixbuf_type(self):
        cell = Cell('test', type=GdkPixbuf.Pixbuf)
        self.assertEqual(cell.mappers[0].prop, 'pixbuf')

    def test_markup(self):
        cell = Cell('test', use_markup=True)
        self.assertEqual(cell.mappers[0].prop, 'markup')

    def test_stock_type(self):
        cell = Cell('test', use_stock=True)
        self.assertEqual(cell.mappers[0].prop, 'stock-id')

    def test_secondar_mappers(self):
        cell = Cell('test', mapped={'markup': 'markup_attr'})
        self.assertEqual(len(cell.mappers), 2)
        #XXX cellmapper needs death
        m = cell.mappers[0].mappers[0]
        self.assertEqual(m.prop, 'markup')
        self.assertEqual(m.attr, 'markup_attr')

    def test_cell_ellipsize(self):
        cell = Cell('test', ellipsize=Pango.EllipsizeMode.END)
        renderer = cell.create_renderer(None, None)
        el = renderer.get_property('ellipsize')
        self.assertEqual(el, Pango.EllipsizeMode.END)

    def test_cell_toggle(self):
        cell = Cell('test', use_checkbox=True)
        renderer = cell.create_renderer(None, None)
        self.assertFalse(renderer.get_property('radio'))

    def test_cell_radio(self):
        cell = Cell('test', use_radio=True)
        renderer = cell.create_renderer(None, None)
        self.assertTrue(renderer.get_property('radio'))

    def test_cell_radio_checkbox_both(self):
        # radio and checkbox, checkbox should win
        cell = Cell('test', use_checkbox=True, use_radio=True)
        renderer = cell.create_renderer(None, None)
        self.assertFalse(renderer.get_property('radio'))

    def test_cell_spin(self):
        cell = Cell('test', type=int, use_spin=True)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('adjustment').get_property('lower'), 0)

    def test_cell_spin_digits_int(self):
        cell = Cell('test', type=int, use_spin=True)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('digits'), 0)

    def test_cell_spin_digits_float(self):
        cell = Cell('test', type=float, use_spin=True)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('digits'), 2)

    def test_cell_spin_digits(self):
        cell = Cell('test', type=float, use_spin=True, digits=5)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('digits'), 5)

    def test_cell_spin_min(self):
        cell = Cell('test', type=int, use_spin=True, min=5)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('adjustment').get_property('lower'), 5)

    def test_cell_spin_max(self):
        cell = Cell('test', type=int, use_spin=True, max=5)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('adjustment').get_property('upper'), 5)

    def test_cell_spin_step(self):
        cell = Cell('test', type=int, use_spin=True, step=5)
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('adjustment').get_property('step-increment'), 5)

    def test_cell_progress(self):
        cell = Cell('test', type=int, use_progress=True)
        renderer = cell.create_renderer(None, None)
        self.assertLess(renderer.get_property('pulse'), 1)

    def test_cell_progress_text(self):
        cell = Cell('test', type=int, use_progress=True, progress_text='hello')
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('text'), 'hello')

    def test_cell_props(self):
        cell = Cell('test', cell_props={'size': 100})
        renderer = cell.create_renderer(None, None)
        self.assertEqual(renderer.get_property('size'), 100)


if __name__ == '__main__':
    unittest.main()
