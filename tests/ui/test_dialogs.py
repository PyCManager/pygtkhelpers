import unittest
import gi
import os

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GLib
from pyGtkHelpers.ui.dialogs import info, open


def with_response(response, starter, *k, **kw):
    def before_run(dialog):
        def idle_fun():
            dialog.response(response)
        GLib.idle_add(idle_fun)

    return starter(*k, _before_run=before_run, **kw)


def test_info():
    with_response(1, info, 'hi')


class TestDialogs(unittest.TestCase):

    def test_filechooser_open(self):
        tmpdir = GLib.get_tmp_dir()
        filename = str(os.path.join(tmpdir, 'somefile.txt'))

        def before_run(dialog):
            dialog.set_current_folder(str(tmpdir))

            def idle_fun():
                dialog.response(Gtk.ResponseType.OK)
                assert dialog.select_filename(filename)

                dialog.get_action_area().get_children()[0].emit('clicked')
            GLib.idle_add(idle_fun)

        res = open(_before_run=before_run)
        self.assertEqual(res, filename)


if __name__ == '__main__':
    unittest.main()
