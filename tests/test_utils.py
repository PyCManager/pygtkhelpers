import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject
from pyGtkHelpers.utils import gsignal, gproperty, \
        GObjectUserDataProxy, \
        eformat, MarkupMixin, XFormatter
from pyGtkHelpers.delegates import BaseDelegate


class TestGSignals(unittest.TestCase):

    def testGSignal(self):
        class T1(GObject.GObject):
            __gtype_name__ = 'test1'
            gsignal('testsignal')
            gsignal('b', retval=GObject.TYPE_INT)
            self.assertRaises(TypeError, lambda: gsignal('c', retval=GObject.TYPE_INT, flags=GObject.SignalFlags.RUN_FIRST))

        class T3(Gtk.Button):
            gsignal('clicked', 'override')

        t = T1()
        t.connect('testsignal', lambda *a: None)

    def testGProperty(self):

        class T2(BaseDelegate):
            def create_default_toplevel(self):
                return

            __gtype_name__ = 'test2'
            gproperty('a', int, default=0)
            self.assertRaises(TypeError, gproperty, 'b', bool)
            self.assertRaises(TypeError, gproperty, 'c', bool, default='a')
            self.assertRaises(TypeError, gproperty, 'd', bool, nick=1)
            self.assertRaises(TypeError, gproperty, 'e', bool, blurb=1)
            gproperty('f', int, default=10)
            gproperty('g', bool, default=True)
            self.assertRaises(TypeError, gproperty, 'h', Gtk.ArrowType)
            gproperty('i', Gtk.ArrowType, default=Gtk.ArrowType.UP)
            self.assertRaises(TypeError, gproperty, 'j', Gtk.ArrowType, default=1)
            gproperty('k', str)
            gproperty('l', object)
            self.assertRaises(TypeError, gproperty, 'm', object, default=1)
            self.assertRaises(NotImplementedError, gproperty, 'n', Gtk.Label)
            self.assertRaises(TypeError, gproperty, 'o', int, flags=-1)
            gproperty('p', object)

        t = T2()
        print(t)
        self.assertEqual(t.get_property('a'), 0)

    def testDataProxySet(self):
        w = Gtk.Entry()
        data = GObjectUserDataProxy(w)
        data.foo = 123
        self.assertEqual(w.get_data('foo'), 123)

    def testDataProxyGet(self):
        w = Gtk.Entry()
        w.set_data('foo', 123)
        data = GObjectUserDataProxy(w)
        self.assertEqual(data.foo, 123)

    def testDataProxyMissing(self):
        w = Gtk.Entry()
        data = GObjectUserDataProxy(w)
        self.assertEqual(data.foo, None)

    def testDataProxyDelete(self):
        w = Gtk.Entry()
        data = GObjectUserDataProxy(w)
        data.foo = 123
        self.assertEqual(data.foo, 123)
        del data.foo
        self.assertEqual(data.foo, None)

    def testEFormat(self):
        self.assertEqual(eformat('{self!e}', self='<'), '&lt;')

    def testMarkupMixinObj(self):
        class Tested(MarkupMixin):
            format = '{a} 1'
            a = 1
        instance = Tested()

        self.assertEqual(instance.markup, '1 1')

    def testMarkupMixingKwargs(self):
        class Tested(MarkupMixin):
            format = '{a} 1'
            # markup kwargs should override attributes
            a = 2

            def markup_kwargs(self):
                return {'a': '1'}

        instance = Tested()

        assert instance.markup == '1 1'

    def testXFormatterExtraConverters(self):
        formatter = XFormatter(a=lambda x: str(x)*2)
        result = formatter.format('{0!a}', 'x')

        self.assertEqual(result, 'xx')

    def testMarkupMixinExtraFormatter(self):
        class Tested(MarkupMixin):
            format = '{a!c}'
            markup_converters = {
                'c': lambda x: x.capitalize(),
            }
            a = 'a'

        instance = Tested()
        self.assertEqual(instance.markup, 'A')


if __name__ == '__main__':
    unittest.main()
