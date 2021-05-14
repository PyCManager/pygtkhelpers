# -*- coding: utf-8 -*-
"""
    pyGtkHelpers.utils.redirected
    ~~~~~~~~~~~~~~~~~~

    Utilities for handling some of the wonders of PyGTK.
    gproperty and gsignal are mostly taken from kiwi.utils

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

import os
import sys


from contextlib import contextmanager


def fileno(file_or_fd):
    fd = getattr(file_or_fd, 'fileno', lambda: file_or_fd)()
    if not isinstance(fd, int):
        raise ValueError("Expected a file (`.fileno()`) or a file descriptor")
    return fd


@contextmanager
def stdout_redirected(to=os.devnull, stdout=None):
    if stdout is None:
        stdout = sys.stdout

    stdout_fd = fileno(stdout)
    # copy stdout_fd before it is overwritten
    # NOTE: `copied` is inheritable on Windows when duplicating a standard stream
    with os.fdopen(os.dup(stdout_fd), 'wb') as copied:
        stdout.flush()  # flush library buffers that dup2 knows nothing about
        try:
            os.dup2(fileno(to), stdout_fd)  # $ exec >&to
        except ValueError:  # filename
            with open(to, 'wb') as to_file:
                os.dup2(to_file.fileno(), stdout_fd)  # $ exec > to
        try:
            # allow code to be run with the redirected stdout
            yield stdout
        finally:
            # restore stdout to its previous value
            # NOTE: dup2 makes stdout_fd inheritable unconditionally
            stdout.flush()
            os.dup2(copied.fileno(), stdout_fd)  # $ exec >&copied


@contextmanager
def to_devnull(target):
    # Redirect c extensions print statements to null
    old_stderr_fno = os.dup(sys.stderr.fileno())
    devnull = open(os.devnull, 'w')
    os.dup2(devnull.fileno(), target)
    yield
    os.dup2(old_stderr_fno, target)
    devnull.close()


def no_stdout():
    return to_devnull(1)


def no_stderr():
    return to_devnull(2)
