import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject
from pyGtkHelpers.delegates import SlaveView, ToplevelView, BaseDelegate, \
    WindowView
from pyGtkHelpers.utils import refresh_gui, gproperty


class _Delegate1(BaseDelegate):
    pass


class _Delegate2(BaseDelegate):

    def create_default_toplevel(self):
        pass


class _Delegate3(BaseDelegate):

    builder_file = 'test_slave.ui'

    def create_default_toplevel(self):
        pass


class _BuilderConnectHandler(SlaveView):

    builder_file = 'test_slave_builder_connect.ui'

    def the_dammed_handler(self, btn, *k):
        self.clicked = 1


class _TestDelegate(SlaveView):

    def create_ui(self):
        self.clicked = False
        self.main = Gtk.Button()
        self.widget.pack_start(self.main)

    def on_main__clicked(self, button):
        self.clicked = True


class _Delegate5(SlaveView):

    def create_ui(self):
        self.clicked = False
        self.main = Gtk.Button()
        self.widget.pack_start(self.main)

    def after_main__clicked(self, button):
        self.clicked = True


class _Delegate6(ToplevelView):

    builder_file = 'test_slave.ui'
    toplevel_name = 'label1'


class _Delegate7(SlaveView):

    gproperty('a', int)
    gproperty('b', int)

    def set_property_b(self, value):
        self._b = value

    def get_property_b(self):
        return 17


class _TestUIDelegate(SlaveView):

    builder_file = 'test_slave.ui'


class _TestUIDelegate2(SlaveView):

    builder_path = 'tests/ui/test_slave.ui'


class _TestUIMainDelegate(ToplevelView):

    builder_file = 'test_slave.ui'


class _TestUIDelegateBindSignalError(SlaveView):
    def create_ui(self):
        self.button = Gtk.Button("test")
        self.widget.pack_start(self.button)

    def on_button__clacled(self, button):
        pass


class _TestUIDelegateSignalTargetMissing(SlaveView):
    def on_button__clicked(self, button):
        pass


class TestUIDelegate(unittest.TestCase):

    def test_delegate1(self):
        self.assertRaises(NotImplementedError, _Delegate1)

    def test_delegate2(self):
        t = _Delegate2()

    def test_delegatge3(self):
        self.assertRaises(NotImplementedError, _Delegate3)

    def test_object_connect(self):
        d = _BuilderConnectHandler()
        d.button1.emit('clicked')
        self.assertTrue(d.clicked)

    def test_no_ui_file(self):
        d = SlaveView()


class MissingUiDelegate(SlaveView):
    builder_file = 'missing.ui'


class MissingUiDelegate2(SlaveView):
    builder_path = 'missing.ui'


class TestMissingUiDelegate(unittest.TestCase):

    def test_missing_uifile(self):
        self.assertRaises(LookupError, MissingUiDelegate)

    def test_missing_uipath(self):
        self.assertRaises(LookupError, MissingUiDelegate2)

    def test_signals_list(self):
        d = _TestDelegate()
        self.assertTrue(list(d._get_all_handlers()))

    def test_ui_delegatge(self):
        d = _TestUIDelegate()
        self.assertTrue(hasattr(d, 'label1'))

    def test_ui_delegatge2(self):
        d = _TestUIDelegate2()
        self.assertTrue(hasattr(d, 'label1'))

    def test_ui_delegatge3(self):
        d = _TestUIMainDelegate()
        self.assertTrue(hasattr(d, 'label1'))

    def test_ui_main_delegate_bad_toplevel(self):
        d = _Delegate6()
        self.assertTrue(GObject.type_is_a(d._toplevel, Gtk.Window))


    def test_signal_handle(self):
        d = _TestDelegate()
        d.main.clicked()
        refresh_gui()
        self.assertTrue(d.clicked)

    def test_signal_after(self):
        d = _Delegate5()
        d.main.clicked()
        refresh_gui()
        self.assertTrue(d.clicked)

    def test_props(self):
        d = _Delegate7()
        self.assertEqual(d.get_property('a'), 0)
        d.set_property('a', 19)
        self.assertEqual(d.get_property('a'), 19)
        d.set_property('b', 9)
        self.assertEqual(d._b == 9)
        self.assertEqual(d.get_property('b'), 17)

    def test_bind_sinal_error_warning(self):
        self.assertRaises(TypeError, _TestUIDelegateBindSignalError)


    def test_find_signal_target_warning(self):
        self.assertRaises(LookupError, _TestUIDelegateSignalTargetMissing)


class NeedsBaseClassUIFileSearch(_TestUIDelegate):
    __module__ = 'a.big.lie'


class TestUiFileLoadFromBase(unittest.TestCase):

    def test_uifile_load_from_base(self):
        """
        a delegate should search base classes for ui definitions
        first match goes
        """
        NeedsBaseClassUIFileSearch()


# slave and master
class S(SlaveView):
    def create_ui(self):
        self.entry = Gtk.Entry()
        self.widget.add(self.entry)


class W(WindowView):
    def create_ui(self):
        self.slave = self.add_slave(S(), 'widget')


class TestSlaveDelegate(unittest.TestCase):
    def test_addslave_delegate(self):
        w = W()
        self.assertTrue(len(w.slaves))

    def test_slavewidget_added(self):
        w = W()
        self.assertTrue(w.widget.get_child())

    def test_missing_container(self):
        w = WindowView()
        self.assertRaises(AttributeError, w.add_slave, S(), 'banana')

    def test_set_title(self):
        w = WindowView()
        w.set_title('test')


if __name__ == '__main__':
    unittest.main()
