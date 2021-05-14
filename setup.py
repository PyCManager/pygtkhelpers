try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools import Extension
from distutils.command import build_ext

import os
import sys
import platform
import subprocess
import versioneer


#def pkc_get_dirs(option, *names):
    #output = getoutput(' '.join(['pkg-config', option] + list(names)))
    #return output.replace(option[-2:], '').split()

moo = Extension(
    'moo',
    ['contrib/moo/%s' % c for c in [
        'moopane.c',
        'moopaned.c',
        'moobigpaned.c',
        'marshals.c',
        'moo-pygtk.c',
        'moo-stub.c',
        'moopython-utils.c',
    ]],
    #include_dirs=pkc_get_dirs('--cflags-only-I', 'gtk+3', 'pygobject3'),
    #libraries=pkc_get_dirs('--libs-only-l', 'gtk+3', 'pygobject3'),
    #library_dirs=pkc_get_dirs('--libs-only-L', 'gtk+3', 'pygobject3'),
)


class BuildExt(build_ext):
    def build_extension(self, ext):
        if ext.name == 'moo':
            subprocess.check_call(
                ['make', 'prepare'],
                cwd=os.path.join(os.path.dirname(__file__), 'contrib/moo')
            )
        build_ext.build_extension(self, ext)

short_description = """
PyGTKHelpers is a library to assist the building of PyGTK applications.
""".strip()

long_description = """
# Note #

This project is a fork of [this project][1], written by Ali Afshar
<aafshar@gmail.com>.

# Description #

PyGTKHelpers is a library to assist the building of PyGTK applications. It is
intentionally designed to be *non-frameworky*, and blend well with your
particular style of PyGTK development.

PyGTKHelpers provides a number of widespread features including: View
delegation, MVC, mixed GtkBuilder/Python views, widget proxying, signal
auto-connection, object-base lists and trees, a number of helper widgets,
utility functions for assisting creating new GObject types, unit testing
helpers and utilities to help debug PyGTK applications.


[1]: https://pythonhosted.org/pygtkhelpers/
""".strip()


install_requires = [
    #'cairo-helpers>=0.2.post1',
    'flatland>=0.9.1',
    'ipython-helpers>=0.5',
    'si-prefix>=1.2.2',
    #'svg-model>=0.5.post18',
    'numpy',
    'jsonschema',
    'pandas',
    'Pillow',
    'six',
    'pint',
    'lxml',
    'trollius'
    #'zbar-lite'
]

# Platform-specific package requirements.
if platform.system() == 'Windows':
    install_requires += []
else:
    try:
        import gi
    except ImportError:
        print(('Please install Python bindings for Gtk3 using your systems package manager.'), file=sys.stderr)


setup(name='wheeler.pyGtkHelpers',
      version=versioneer.get_version(),
      cmdclass={
          'build_ext': BuildExt,
          'build_py': versioneer.get_cmdclass()
      },
      author='Patrick LUZOLO',
      author_email='eldorplus@gmail.com',
      url='https://github.com/PyCManager/pygtkhelpers',
      description=short_description,
      long_description=long_description,
      license='LGPL-3.0',
      install_requires=install_requires,
      ext_modules=[moo],
      packages=['pyGtkHelpers', 'pyGtkHelpers.ui', 'pyGtkHelpers.debug',
                'pyGtkHelpers.ui.objectlist', 'pyGtkHelpers.ui.views'],
      package_data={'pyGtkHelpers': ['ui/glade/*.glade',
                                     'ui/views/glade/*.glade']})
