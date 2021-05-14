import unittest
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from pyGtkHelpers.utils import refresh_gui
from pyGtkHelpers.test import CheckCalled
from pyGtkHelpers.forms import FormView, Field
from flatland import Dict, String, Integer, Boolean


class PersonForm(FormView):

    schema_type = Dict.of(
        String.named('name'),
        Integer.named('age'),
        Boolean.named('friendly'),
    )


class TestForm(unittest.TestCase):

    def test_form_fields(self):
        f = PersonForm()
        self.assertIsInstance(f.name, Gtk.Entry)
        self.assertIsInstance(f.age, Gtk.SpinButton)
        self.assertIsInstance(f.friendly, Gtk.CheckButton)

    def test_form_field_value_changed(self):
        f = PersonForm()
        check = CheckCalled(f.form.proxies, 'changed')
        f.name.set_text('hello')
        self.assertEqual(check.called[2], 'name')
        self.assertEqual(check.called[3], 'hello')

    def test_update_schema_value(self):
        f = PersonForm()
        self.assertEqual(f.form.schema['name'].value, None)
        f.name.set_text('hello')
        self.assertEqual(f.form.schema['name'].value, 'hello')

    def test_update_schema_value_typed(self):
        f = PersonForm()
        self.assertEqual(f.form.schema['friendly'].value, None)
        f.friendly.set_active(True)
        self.assertEqual(f.form.schema['friendly'].value, True)
        f.friendly.set_active(False)
        self.assertEqual(f.form.schema['friendly'].value, False)


if __name__ == '__main__':
    unittest.main()
