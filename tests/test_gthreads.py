import unittest
import gi

gi.require_version('Gtk', '3.0')

from pyGtkHelpers.utils import refresh_gui
from pyGtkHelpers.gthreads import AsyncTask, GeneratorTask
from pyGtkHelpers.gthreads import gcall, invoke_in_mainloop


class TestGThreads(unittest.TestCase):

    def test_async_task(self):
        data = []

        def do():
            data.append(1)
            return 2, 3

        def done(*k):
            data.extend(k)

        GeneratorTask(do, done).start()
        refresh_gui()
        self.assertEqual(data, [1, 2, 3])

    def test_generator_task(self):
        data = []

        def do():
            for i in range(10):
                yield i

        def work(val):
            data.append(val)

        def done():
            data.extend(data)

        GeneratorTask(do, work, done).start()
        refresh_gui()

        self.assertEqual(data, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_gcall(self):
        data = []

        def doit():
            gcall(data.append, 1)

        AsyncTask(doit).start()
        refresh_gui(.1)
        self.assertEqual(data, [1])

    def test_invoke_in_mainloop(self):
        data = []

        def doit():
            invoke_in_mainloop(data.append, 1)
            assert invoke_in_mainloop(len, data) == 1

        AsyncTask(doit).start()
        # timeout needed for asynctask cleanup
        refresh_gui(.1)
        self.assertEqual(data, [1])


if __name__ == '__main__':
    unittest.main()
