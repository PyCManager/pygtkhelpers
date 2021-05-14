import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.ui.objectlist import ObjectList


class TestBuildSimple(unittest.TestCase):

    def test_build_simple(self):
        uidef = '''
            <interface>
              <object class="PyGTKHelpersObjectList" id="test">
              </object>
            </interface>
        '''
        b = Gtk.Builder()
        b.add_from_string(uidef)
        objectlist = b.get_object('test')
        self.assertIsInstance(objectlist, ObjectList)


if __name__ == '__main__':
    unittest.main()
