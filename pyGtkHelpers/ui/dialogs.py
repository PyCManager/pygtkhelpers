# -*- coding: utf-8 -*-

"""
    pyGtkHelpers.ui.dialogs
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Dialog helpers

    largely inspired by kiwi.ui.dialogs

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

# XXX: i18n
import itertools as it
import os
import threading
import collections

from itertools import cycle
from functools import partial
from gi.repository import GLib, Gtk, Gdk

image_types = {
    Gtk.MessageType.INFO: Gtk.STOCK_DIALOG_INFO,
    Gtk.MessageType.WARNING: Gtk.STOCK_DIALOG_WARNING,
    Gtk.MessageType.QUESTION: Gtk.STOCK_DIALOG_QUESTION,
    Gtk.MessageType.ERROR: Gtk.STOCK_DIALOG_ERROR
}

button_types = {
    Gtk.ButtonsType.NONE: (),
    Gtk.ButtonsType.OK: (
        Gtk.STOCK_OK,
        Gtk.ResponseType.OK,
    ),
    Gtk.ButtonsType.CLOSE: (
        Gtk.STOCK_CLOSE,
        Gtk.ResponseType.CLOSE,
    ),
    Gtk.ButtonsType.CANCEL: (
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
    ),
    Gtk.ButtonsType.YES_NO: (
        Gtk.STOCK_NO,
        Gtk.ResponseType.NO,
        Gtk.STOCK_YES,
        Gtk.ResponseType.YES,
    ),
    Gtk.ButtonsType.OK_CANCEL: (
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OK,
        Gtk.ResponseType.OK,
    ),
}


def _destroy(win):
    # XXX: util?
    win.destroy()
    if not Gtk.main_level():
        from pyGtkHelpers.utils import refresh_gui
        refresh_gui()


class AlertDialog(Gtk.Dialog):
    def __init__(self, parent, flags,
                 type=Gtk.MessageType.INFO,
                 buttons=None,
                 ):
        # XXX: better errors
        assert type in image_types, 'not a valid type'
        assert buttons in button_types, 'not a valid set of buttons'

        Gtk.Dialog.__init__(self, ' ', parent, flags)
        self.set_border_width(5)
        self.set_has_separator(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)

        self.primary = Gtk.Label()
        self.secondary = Gtk.Label()
        self.details = Gtk.Label()
        self.image = Gtk.image_new_from_stock(
            image_types[type],
            Gtk.ICON_SIZE_DIALOG
        )
        self.image.set_alignment(0.0, 0.5)
        self.primary.set_use_markup(True)

        for label in (self.primary, self.secondary, self.details):
            label.set_line_wrap(True)
            label.set_selectable(True)
            label.set_alignment(0.0, 0.5)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hbox.set_border_width(5)
        hbox.pack_start(self.image, False, False)

        self.label_vbox = vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hbox.pack_start(vbox, False, False)
        vbox.pack_start(self.primary, False, False)
        vbox.pack_start(self.secondary, False, False)

        self.expander = Gtk.expander_new_with_mnemonic(
            'show more _details'
        )
        self.expander.set_spacing(5)
        self.expander.add(self.details)
        vbox.pack_start(self.expander, False, False)
        self.vbox.pack_start(hbox, False, False)
        hbox.show_all()
        self.expander.hide()
        self._buttons = button_types[buttons]
        self.add_buttons(*self._buttons)

    def set_primary(self, text):
        # XXX: escape
        self.primary.set_markup('<span weight="bold" size="larger">%s</span>' %
                                (text,))

    def set_secondary(self, text):
        self.set_secondary.set_markup(text)

    def set_details(self, text):
        self.details.set_markup(text)
        self.expander.show()

    def set_details_widget(self, widget):
        self.expander.remove(self.details)
        self.details = widget
        self.expander.add(widget)
        self.expander.show()


def _message_dialog(type, short,
                    long=None,
                    parent=None,
                    buttons=Gtk.ButtonsType.OK,
                    default=None,  # XXX: kiwi had -1 there, why?
                    alt_button_order=None,
                    _before_run=None):  # for unittests
    if buttons in button_types:
        dialog_buttons = buttons
        buttons = []
    else:
        assert buttons is None or isinstance(buttons, tuple)
        dialog_buttons = Gtk.ButtonsType.NONE

    assert parent is None or isinstance(parent, Gtk.Window)

    dialog = AlertDialog(parent=parent, flags=Gtk.DialogFlags.MODAL, type=type,
                         buttons=dialog_buttons)
    dialog.set_primary(short)

    if long:
        # XXX: test all cases
        if isinstance(long, Gtk.Widget):
            dialog.set_details_widget(long)
        elif isinstance(long, (str, bytes)):
            dialog.set_details(long)
        else:
            raise TypeError('long must be a string or a Widget, not %r' % long)

    if default is not None:
        dialog.set_default_response(default)
    if parent:
        dialog.set_transient_for(parent)
        dialog.set_modal(True)

    if alt_button_order:
        dialog.set_alternative_button_order(alt_button_order)
    if _before_run is not None:
        _before_run(dialog)

    response = dialog.run()
    _destroy(dialog)
    return response


def add_filters(dialog, filters):
    for f in filters:
        filter_text = Gtk.FileFilter()
        filter_text.set_name(f['name'])
        if 'mime_type' in f:
            mime_types = f['mime_type']
            if not isinstance(mime_types, collections.Iterable):
                mime_types = [mime_types]
            for mime_type in mime_types:
                filter_text.add_mime_type(mime_type)
        elif 'pattern' in f:
            patterns = f['pattern']
            if not isinstance(patterns, collections.Iterable):
                patterns = [patterns]
            for pattern in patterns:
                print('add pattern: "%s"' % pattern)
                filter_text.add_pattern(pattern)
        dialog.add_filter(filter_text)


def simple(type, short, long=None,
           parent=None, buttons=Gtk.ButtonsType.OK, default=None, **kw):
    """A simple dialog

    :param type: The type of dialog
    :param short: The short description
    :param long: The long description
    :param parent: The parent Window to make this dialog transient to
    :param buttons: A buttons enum
    :param default: A default response
    """
    if buttons == Gtk.ButtonsType.OK:
        default = Gtk.ResponseType.OK
    return _message_dialog(type, short, long, parent=parent, buttons=buttons,
                           default=default, **kw)


def open_file_chooser(
        title,
        parent=None,
        patterns=None,
        folder=None,
        filter=None,
        multiple=False,
        _before_run=None,
        action=None
):
    """An open dialog.

    :param parent: window or None
    :param patterns: file match patterns
    :param folder: initial folder
    :param filter: file filter

    Use of filter and patterns at the same time is invalid.
    """

    assert not (patterns and filter)
    if multiple:
        if action is not None and action != Gtk.FileChooserAction.OPEN:
            raise ValueError('`multiple` is only valid for the action '
                             '`Gtk.FileChooserAction.OPEN`.')
        action = Gtk.FileChooserAction.OPEN
    else:
        assert action is not None
    file_chooser = Gtk.FileChooserDialog(
        title=title,
        transient_for=parent,
        action=action
    )
    file_chooser.add_buttons(
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN,
        Gtk.ResponseType.OK
    )
    if multiple:
        file_chooser.set_select_multiple(True)

    if patterns or filter:
        if not filter:
            filter = Gtk.FileFilter()
            for pattern in patterns:
                filter.add_pattern(pattern)
        file_chooser.set_filter(filter)
    file_chooser.set_default_response(Gtk.ResponseType.OK)

    if folder:
        file_chooser.set_current_folder(folder)

    try:
        if _before_run is not None:
            _before_run(file_chooser)
        response = file_chooser.run()
        if response not in (Gtk.ResponseType.OK, Gtk.ResponseType.NONE):
            return

        if multiple:
            return file_chooser.get_filenames()
        else:
            return file_chooser.get_filename()
    finally:
        _destroy(file_chooser)


def ask_overwrite(filename, parent=None, **kw):
    submsg1 = 'A file named "%s" already exists' % os.path.abspath(filename)
    submsg2 = 'Do you wish to replace it with the current one?'
    text = ('<span weight="bold" size="larger">%s</span>\n'
            '\n%s\n' % (submsg1, submsg2))
    result = _message_dialog(Gtk.MessageType.ERROR, text, parent=parent,
                             buttons=((Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),
                                      (_("Replace"), Gtk.ResponseType.YES)), **kw)
    return result == Gtk.ResponseType.YES


def save(
        title='Save',
        parent=None,
        current_name='',
        folder=None,
        _before_run=None,
        _before_overwrite=None
):
    """Displays a save dialog."""
    file_chooser = Gtk.FileChooserDialog(
        title=title,
        transient_for=parent,
        action=Gtk.FileChooserAction.SAVE
    )
    file_chooser.add_buttons(
        Gtk.STOCK_CANCEL,
        Gtk.ResponseType.CANCEL,
        Gtk.STOCK_SAVE,
        Gtk.ResponseType.OK
    )
    if current_name:
        file_chooser.set_current_name(current_name)
    file_chooser.set_default_response(Gtk.ResponseType.OK)

    if folder:
        file_chooser.set_current_folder(folder)

    path = None
    while True:
        if _before_run:
            _before_run(file_chooser)
            _before_run = None  # XXX: find better implications
        response = file_chooser.run()
        if response != Gtk.ResponseType.OK:
            path = None
            break

        path = file_chooser.get_filename()
        if not os.path.exists(path):
            break

        if ask_overwrite(path, parent, _before_run=_before_overwrite):
            break
        _before_overwrite = None  # XXX: same
    _destroy(file_chooser)
    return path


def input(
        title,
        value=None,
        label=None,
        parent=None,
        _before_run=None
):
    d = Gtk.Dialog(title=title, buttons=button_types[Gtk.ButtonsType.OK_CANCEL])

    e = Gtk.Entry()
    if value:
        e.set_text(value)

    if label is None:
        e.show()
        d.vbox.pack_start(e)
    else:
        hbox = Gtk.HBox()
        hbox.set_spacing(6)
        hbox.set_border_width(6)
        hbox.add(Gtk.Label(label=label))
        hbox.add(e)
        hbox.show_all()
        d.vbox.add(hbox)

    if parent:
        d.set_transient_for(parent)

    if _before_run:
        _before_run(d)
    r = d.run()
    res = e.get_text()
    d.hide()
    d.destroy()
    if r == Gtk.ResponseType.OK:
        return res


open = partial(
    open_file_chooser,
    title='Open',
    action=Gtk.FileChooserAction.OPEN
)

select_folder = partial(
    open_file_chooser,
    title='Select folder',
    action=Gtk.FileChooserAction.SELECT_FOLDER
)

# Show an error dialog, see :func:`~pyGtkHelpers.ui.dialogs.simple` parameters
error = partial(simple, Gtk.MessageType.ERROR)

# Show an info dialog, see :func:`~pyGtkHelpers.ui.dialogs.simple` parameters
info = partial(simple, Gtk.MessageType.INFO)

# Show a warning dialog, see :func:`~pyGtkHelpers.ui.dialogs.simple` parameters
warning = partial(simple, Gtk.MessageType.WARNING)

#  A yes/no question dialog, see :func:`~pyGtkHelpers.ui.dialogs.simple`
#  parameters
yesno = partial(
    simple,
    Gtk.MessageType.WARNING,
    default=Gtk.ResponseType.YES,
    buttons=Gtk.ButtonsType.YES_NO,
)


def animation_dialog(images, delay_s=1., loop=True, **kwargs):
    """
    .. versionadded:: v0.19

    Parameters
    ----------
    images : list
        Filepaths to images or :class:`Gtk.Pixbuf` instances.
    delay_s : float, optional
        Number of seconds to display each frame.

        Default: ``1.0``.
    loop : bool, optional
        If ``True``, restart animation after last image has been displayed.

        Default: ``True``.

    Returns
    -------
    Gtk.MessageDialog
        Message dialog with animation displayed in `Gtk.Image` widget when
        dialog is run.
    """

    def _as_pixbuf(image):
        if isinstance(image, collections.Iterable):
            return Gtk.gdk.pixbuf_new_from_file(image)
        else:
            return image

    pixbufs = map(_as_pixbuf, images)

    # Need this to support background thread execution with GTK.
    Gdk.threads_init()

    dialog = Gtk.MessageDialog(**kwargs)

    # Append image to dialog content area.
    image = Gtk.Image()
    content_area = dialog.get_content_area()
    content_area.pack_start(image)
    content_area.show_all()

    stop_animation = threading.Event()

    def _stop_animation(*args):
        stop_animation.set()

    def _animate(dialog):
        def __animate():
            if loop:
                frames = cycle(pixbufs)
            else:
                frames = pixbufs

            for pixbuf_i in frames:
                GLib.idle_add(image.set_from_pixbuf, pixbuf_i)
                if stop_animation.wait(delay_s):
                    break

        thread = threading.Thread(target=__animate)
        thread.daemon = True
        thread.start()

    dialog.connect('destroy', _stop_animation)
    dialog.connect('show', _animate)
    return dialog


"""
def yesno(message, title=None):
    if title is None:
        title = message
        message = None

    dialog = Gtk.Dialog(title, None, 0,
                        (Gtk.STOCK_NO, Gtk.ResponseType.NO,
                         Gtk.STOCK_YES, Gtk.ResponseType.YES))

    if message is not None:
        label = Gtk.Label(label=message)
        box = dialog.get_content_area()
        hbox = Gtk.HBox()
        hbox.pack_start(label, False, False, 10)
        box.pack_start(hbox, False, False, 10)
        box.show_all()
    dialog.set_size_request(150, 50)

    response = dialog.run()
    dialog.destroy()
    return response
"""
