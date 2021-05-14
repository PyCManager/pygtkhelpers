import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.ui.objectlist import Column


class MockTooltip(object):
    def set_text(self, text):
        self.text = text

    def set_markup(self, markup):
        self.markup = markup

    def set_custom(self, custom):
        self.custom = custom

    def set_icon(self, icon):
        self.pixbuf = icon

    def set_icon_from_stock(self, stock, size):
        self.stock = stock
        self.size = size

    def set_icon_from_icon_name(self, iconname, size):
        self.iconname = iconname
        self.size = size


class Fruit(object):
    attr = 'value'


class TestToolTip(unittest.TestCase):

    def test_tooltip_type_text_value(self):
        c = Column('test', tooltip_value='banana')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.text, 'banana')

    def test_tooltip_type_text_attr(self):
        c = Column('test', tooltip_attr='attr')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.text, 'value')

    def test_tooltip_type_markup_value(self):
        c = Column('test', tooltip_value='banana', tooltip_type='markup')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.markup, 'banana')

    def test_tooltip_type_markup_attr(self):
        c = Column('test', tooltip_attr='attr', tooltip_type='markup')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.markup, 'value')

    def test_tooltip_type_stock_value(self):
        c = Column('test', tooltip_value='banana', tooltip_type='stock')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.stock, 'banana')

    def test_tooltip_type_stock_attr(self):
        c = Column('test', tooltip_attr='attr', tooltip_type='stock')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.stock, 'value')

    def test_tooltip_type_iconname_value(self):
        c = Column('test', tooltip_value='banana', tooltip_type='iconname')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.iconname, 'banana')

    def test_tooltip_type_iconname_attr(self):
        c = Column('test', tooltip_attr='attr', tooltip_type='iconname')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.iconname, 'value')

    def test_tooltip_type_pixbuf_value(self):
        c = Column('test', tooltip_value='banana', tooltip_type='pixbuf')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.pixbuf, 'banana')

    def test_tooltip_type_pixbuf_attr(self):
        c = Column('test', tooltip_attr='attr', tooltip_type='pixbuf')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.pixbuf, 'value')

    def test_tooltip_type_custom_value(self):
        c = Column('test', tooltip_value='banana', tooltip_type='custom')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.custom, 'banana')

    def test_tooltip_type_custom_attr(self):
        c = Column('test', tooltip_attr='attr', tooltip_type='custom')
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.custom, 'value')

    def test_tooltip_image_size(self):
        c = Column(
            'test',
            tooltip_attr='attr',
            tooltip_type='iconname',
            tooltip_image_size=Gtk.IconSize.MENU)
        t = MockTooltip()
        o = Fruit()
        c.render_tooltip(t, o)
        self.assertEqual(t.iconname, 'value')
        self.assertEqual(t.size, Gtk.IconSize.MENU)


if __name__ == '__main__':
    unittest.main()
