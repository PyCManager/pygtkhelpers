import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.test import CheckCalled
from pyGtkHelpers.utils import refresh_gui
from pyGtkHelpers.proxy import ProxyGroup, GtkEntryProxy


class TestProxyGroup(unittest.TestCase):

    def test_add_proxy(self):
        m = ProxyGroup()
        e = Gtk.Entry()
        p = GtkEntryProxy(e)
        m.add_proxy('foo', p)
        check = CheckCalled(m, 'changed')
        e.set_text('a')
        refresh_gui()
        self.assertEqual(check.called_count, 1)

        p.update('b')
        refresh_gui()
        self.assertEqual(check.called_count, 2)

    def test_add_proxy_for(self):
        m = ProxyGroup()
        e = Gtk.Entry()
        m.add_proxy_for('foo', e)
        check = CheckCalled(m, 'changed')
        e.set_text('a')
        refresh_gui()
        self.assertEqual(check.called_count, 1)

    def test_add_group(self):
        m = ProxyGroup()
        e = Gtk.Entry()
        m.add_proxy_for('foo', e)
        m2 = ProxyGroup()
        m2.add_group(m)
        check = CheckCalled(m2, 'changed')
        e.set_text('a')
        self.assertEqual(check.called_count, 1)


if __name__ == '__main__':
    unittest.main()
