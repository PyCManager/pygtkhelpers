# -*- coding: utf-8 -*-

"""
    pyGtkHelpers.ui.notebook
    ~~~~~~~~~~~~~~~

    Notebook.

    :copyright: 2021 by pyGtkHelpers Authors
    :license: LGPL 2 or later (see README/COPYING/LICENSE)
"""

import os
import collections
import webbrowser

from gi.repository import Gtk
from pathlib import Path
from pyGtkHelpers.delegates import SlaveView
from pyGtkHelpers.ui.dialogs import yesno, add_filters
from pyGtkHelpers.ui.session import SessionManager


class NotebookManagerView(SlaveView):
    def __init__(self, notebook_dir=None, template_dir=None):
        super(NotebookManagerView, self).__init__()
        if notebook_dir is None:
            notebook_dir = os.getcwd()
        self.notebook_dir = Path(notebook_dir).resolve()
        self.template_dir = template_dir
        self.notebook_manager = SessionManager()

    def sessions_dialog(self):
        session_list = NotebookManagerList(self.notebook_manager)
        dialog = Gtk.Dialog(title='Notebook session manager',
                            parent=self.parent,
                            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_transient_for(self.parent)
        dialog.get_content_area().pack_start(session_list.widget)
        return dialog

    def create_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        new_button = Gtk.Button(label='New...')
        open_button = Gtk.Button(label='Open...')
        manager_button = Gtk.Button(label='Manage sessions...')
        new_button.connect('clicked', self.on_new)
        open_button.connect('clicked', self.on_open)
        manager_button.connect('clicked', self.on_manager)

        box.pack_end(new_button, False, False, 0)
        box.pack_end(open_button, False, False, 0)
        box.pack_end(manager_button, False, False, 0)
        self.widget.pack_start(box, False, False, 0)

        self.parent = None
        parent = self.widget.get_parent()
        while parent is not None:
            self.parent = parent
            parent = parent.get_parent()
        self.widget.show_all()

    def get_parent(self):
        self.parent = None
        parent = self.widget.get_parent()
        while parent is not None:
            self.parent = parent
            parent = parent.get_parent()
        return self.parent

    def on_manager(self, button):
        parent = self.get_parent()
        dialog = self.sessions_dialog()
        dialog.show_all()
        if parent is not None:
            parent.set_sensitive(False)
        dialog.run()
        dialog.destroy()
        if parent is not None:
            parent.set_sensitive(True)

    def on_open(self, button):
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                   Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog = Gtk.FileChooserDialog(
            "Open notebook",
            self.parent,
            Gtk.FileChooserAction.OPEN,
            buttons
        )
        add_filters(dialog, [{'name': 'IPython notebook (*.ipynb)',
                              'pattern': '*.ipynb'}])
        dialog.set_current_folder(self.notebook_dir)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_path = dialog.get_filename()
            self.notebook_manager.open(selected_path)
        dialog.destroy()

    def on_new(self, button):
        """
        Copy selected notebook template to notebook directory.

        ## Notes ##

         - An exception is raised if the parent of the selected file is the
           notebook directory.
         - If notebook with same name already exists in notebook directory,
           offer is made to overwrite (the new copy of the file is renamed with
           a count if overwrite is not selected).
        """
        buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                   Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog = Gtk.FileChooserDialog(
            "Select notebook template",
            self.parent,
            Gtk.FileChooserAction.OPEN,
            buttons
        )
        add_filters(dialog, [{'name': 'IPython notebook (*.ipynb)',
                              'pattern': '*.ipynb'}])
        if self.template_dir is not None:
            dialog.set_current_folder(self.template_dir)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_path = Path(dialog.get_filename())
            output_path = self.notebook_dir.joinpath(selected_path.name)

            overwrite = False
            if output_path.is_file():
                # response = yesno('%s already exists. Overwrite?' % output_path.name)
                response = yesno('%s already exists. Overwrite?' % output_path.name,
                                 'Overwrite?')
                if response == Gtk.ResponseType.YES:
                    overwrite = True
                else:
                    counter = 1
                    renamed_path = output_path
                    while renamed_path.is_file():
                        new_name = '%s (%d)%s' % (output_path.name, counter, output_path.suffix)
                        renamed_path = output_path.parent.joinpath(new_name)
                        counter += 1
                    output_path = renamed_path

            self.notebook_manager.launch_from_template(
                selected_path,
                overwrite=overwrite,
                output_name=output_path.name,
                notebook_dir=self.notebook_dir
            )
        dialog.destroy()

    def stop(self):
        self.notebook_manager.stop()

    def __del__(self):
        self.stop()


class NotebookManagerList(SlaveView):
    """
    Display list of running sessions with open button and stop button for each
    session.
    """

    def __init__(self, notebook_manager):
        self.notebook_manager = notebook_manager
        super(NotebookManagerList, self).__init__()

    def create_ui(self):
        # Only list sessions that are currently running.
        sessions = collections.OrderedDict([(k, v)
                                            for k, v in self.notebook_manager
                                            .sessions.iteritems()
                                            if v.is_alive()])
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_size_request(480, 360)

        table = Gtk.Table(len(sessions) + 1, 4)

        header_y_padding = 5
        x_padding = 20
        y_padding = 2

        for k, header in enumerate(['Directory', 'URL']):
            label = Gtk.Label()
            label.set_markup('<b>%s</b>' % header)
            table.attach(label, k, k + 1, 0, 1,
                         xoptions=Gtk.AttachOptions.SHRINK,
                         yoptions=Gtk.AttachOptions.SHRINK,
                         xpadding=x_padding,
                         ypadding=header_y_padding)

        for i, (root, session) in enumerate(sessions.items()):
            i += 1
            root = Path(root)
            name_label = Gtk.Label(label=root.name)
            name_label.set_tooltip_text(str(root))
            url_label = Gtk.Label(label=session.address)

            stop_button = Gtk.Button(label='Stop')
            stop_button.set_tooltip_text('Stop Jupyter notebook for directory %s' % root)
            open_button = Gtk.Button(label='Open')
            open_button.set_tooltip_text('Open Jupyter notebook for directory %s' % root)

            def open_session(button, session):
                webbrowser.open_new_tab(session.address)

            def stop_session(button, session, widgets):
                session.stop()
                for widget in widgets:
                    table.remove(widget)

            open_button.connect('clicked', open_session, session)
            stop_button.connect('clicked', stop_session, session,
                                (name_label, url_label, open_button,
                                 stop_button))

            for k, widget in enumerate((name_label, url_label, open_button,
                                        stop_button)):
                if isinstance(widget, Gtk.Button):
                    x_padding_k = 0
                else:
                    x_padding_k = x_padding
                table.attach(widget, k, k + 1, i, i + 1,
                             xoptions=Gtk.AttachOptions.SHRINK,
                             yoptions=Gtk.AttachOptions.SHRINK,
                             xpadding=x_padding_k,
                             ypadding=y_padding)
        self.table = table
        scroll_window.add_with_viewport(table)
        self.widget.pack_start(scroll_window, False, False, 0)
