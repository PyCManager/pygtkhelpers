import os
import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.proxy import widget_proxies, StringList, SimpleComboBox
from pyGtkHelpers.utils import refresh_gui


def pytest_generate_tests(metafunc):
    for widget, proxy in widget_proxies.items():
        if 'attr' in metafunc.funcargnames:
            if (not getattr(proxy, 'prop_name', None) or
                    getattr(proxy, 'dprop_name', None)):
                continue
        metafunc.addcall(id=widget.__name__, param=(widget, proxy))


def pytest_funcarg__widget(request):
    'the gtk widget the proxy should use'
    widget_type = request.param[0]
    init_args = widget_initargs.get(widget_type, ())

    widget = widget_type(*init_args)
    setup = widget_setups.get(widget_type)
    if setup is not None:
        setup(widget)
    return widget


def pytest_funcarg__attr(request):
    'the property name the proxy will access on the wrapped widget'
    widget, proxy = request.param
    return proxy.prop_name


def pytest_funcarg__proxy(request):
    'the proxy object that wraps the widget'
    widget = request.getfuncargvalue('widget')
    return request.param[1](widget)


def pytest_funcarg__value(request):
    'the value the test should assign via the proxy'
    try:
        return widget_test_values[request.param[0]]
    except KeyError:
        # self.skipTest("external resource not available")
        unittest.skip('missing defaults for class %s' % request.param[0])


def add_simple_model(widget):
    model = Gtk.ListStore(str, str)
    for name in ['foo', 'test']:
        model.append([name, name])
    widget.set_model(model)
    return widget


def add_range(widget):
    widget.set_range(0, 999)
    return widget


widget_initargs = {
    Gtk.FileChooserButton: ('Title',),
    Gtk.LinkButton: ('',),
    SimpleComboBox: ([('name', 'Name'), ('test', "Der Test")], 'name',),
}

widget_setups = {
    Gtk.ComboBox: add_simple_model,
    Gtk.SpinButton: add_range,
    Gtk.HScale: add_range,
    Gtk.VScale: add_range,
    Gtk.HScrollbar: add_range,
    Gtk.VScrollbar: add_range
}
widget_test_values = {
    Gtk.Entry: 'test',
    Gtk.TextView: 'test',
    Gtk.ToggleButton: True,
    Gtk.CheckButton: True,
    Gtk.CheckMenuItem: True,
    Gtk.RadioButton: True,
    Gtk.ColorButton: Gtk.gdk.color_parse('red'),
    Gtk.SpinButton: 1,
    Gtk.HScale: 100,
    Gtk.VScale: 8.3,
    Gtk.HScrollbar: 8.3,
    Gtk.VScrollbar: 8.3,
    StringList: ['hans', 'peter'],
    Gtk.ComboBox: 'test',
    SimpleComboBox: 'test',
    Gtk.FileChooserButton: __file__,
    Gtk.FileChooserWidget: __file__,
    Gtk.FontButton: 'Monospace 10',
    Gtk.Label: 'Hello',
    Gtk.Image: os.path.join(os.path.dirname(__file__), 'data', 'black.png'),
    Gtk.LinkButton: 'http://pida.co.uk/',
    Gtk.ProgressBar: 0.4,
}


class TestProxy(unittest.TestCase):

    def test_update(self, proxy, value):
        proxy.update(value)

    def test_update_and_read(self, proxy, value):
        proxy.update(value)
        if isinstance(proxy.widget, Gtk.FileChooserButton):
            refresh_gui(0.1, 0.1)
        else:
            refresh_gui()
        data = proxy.read()
        self.assertEqual(data, value)

    def test_update_emits_changed(self, proxy, value):
        data = []
        proxy.connect('changed', lambda p, d: data.append(d))
        proxy.update(value)
        print(data)
        self.assertEqual(len(data), 1)

    def test_widget_update_then_read(self, proxy, widget, attr, value):
        widget.set_property(attr, value)
        self.assertEqual(proxy.read(), value)

    def test_update_internal_wont_emit_changed(self, proxy, value):
        data = []
        proxy.connect('changed', lambda p, d: data.append(d))
        proxy.update_internal(value)
        print(data)
        self.assertEqual(len(data), 0)

    def test_widget_externally_changed_emits(self):
        data = []
        w = Gtk.Entry()
        proxy = widget_proxies[Gtk.Entry](w)
        w.connect('changed', lambda p: data.append(p))
        w.set_text('hello')
        self.assertEqual(len(data), 1)


if __name__ == '__main__':
    unittest.main()
