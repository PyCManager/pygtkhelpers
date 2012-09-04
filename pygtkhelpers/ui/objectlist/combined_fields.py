from copy import deepcopy
import re
import logging

import gtk
from flatland import Form, Integer

from ...utils import gsignal
from ..extra_widgets import get_type_from_schema
from ..form_view_dialog import FormViewDialog
from .uuid_minimal import uuid4
from .column import Column
from . import ObjectList


class RowFields(object):
    '''
    Expose all key/value pairs specified through kwargs as object attributes. 
    This is convenient for use in combination with a pygtkhelpers ObjectList,
    since an ObjectList object uses attribute access to read/write field values.

    >>> row_fields = RowFields(foo='Hello', bar='World')
    >>> row_fields.foo
    'Hello'
    >>> row_fields.bar
    'World'
    >>> row_fields.attrs
    {'foo': 'Hello', 'bar': 'World'}
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __getstate__(self):
        return self.__dict__

    def __getattr__(self, name):
        if not name in dir(self):
            setattr(self, name, None)
        return object.__getattribute__(self, name)

    @property
    def attrs(self):
        return dict([(k, v) for k, v in self.__dict__.items() 
                if k not in ('__members__', '__methods__',
                        '_getAttributeNames')])


class CombinedFields(ObjectList):
    '''
    Given a dictionary mapping of form names to pygtkhelpers Form instances
    create an ObjectList where each field in a form is name-mangled to prevent
    Column attribute conflicts.

    >>> from flatland import Form, String, Integer
    >>> from pprint import pprint
    >>> form1 = Form.of(String.named('my_string_field'), Integer.named('my_int_field'))
    >>> form2 = Form.of(String.named('another_string_field'), Integer.named('another_int_field'))
    >>> forms = {'example_form': form1, 'another_form': form2}

    In this example, we have two forms, each with two fields.

    >>> pprint(dict([(name, form.field_schema_mapping) for name, form in forms.items()])) # doctest:+SKIP
    {'another_form': {u'another_int_field': <class '__main__.Integer'>,
                    u'another_string_field': <class '__main__.String'>},
    'example_form': {u'my_int_field': <class '__main__.Integer'>,
                    u'my_string_field': <class '__main__.String'>}}

    Here we have a dictionary, which assigns each form a name (e.g.,
    'another_form').  Using this dictionary of Form instance values, we can
    create a CombinedFields ObjectList to construct a GTK list view showing all
    fields from all forms combined together.

    >>> combined_fields = CombinedFields(forms, enabled_attrs=None)

    Each form in the specified 'forms' is assigned a Universally Unique
    IDentifier (UUID), which is used to perform name-mangling of form field
    names.

    >>> combined_fields.uuid_mapping # doctest:+SKIP
    {'another_form': 'e4467fe0bd', 'example_form': '196ff80637'}

    Here we can see the mangled field names from both forms (compare to the
    original field names above).

    >>> pprint(combined_fields._full_field_to_field_def) # doctest:+SKIP
    {u'_196ff80637__my_int_field': <class '__main__.Integer'>,
     u'_196ff80637__my_string_field': <class '__main__.String'>,
     u'_e4467fe0bd__another_int_field': <class '__main__.Integer'>,
     u'_e4467fe0bd__another_string_field': <class '__main__.String'>}

    Given these unique field names, a pygtkhelpers.ui.objectlist.Column is
    created for each field where 'attr' is set to the unique field name.  The
    title of a Column is generated by using the original (non-mangled) name of
    each field, while replacing underscores with spaces and capitalizing the
    first word, as shown below.

    >>> pprint([(c.attr, c.title) for c in combined_fields._columns]) # doctest:+SKIP
    [(u'_e4467fe0bd__another_string_field', u'Another string field'),
     (u'_e4467fe0bd__another_int_field', u'Another int field'),
     (u'_196ff80637__my_string_field', u'My string field'),
     (u'_196ff80637__my_int_field', u'My int field')]
    '''
    field_set_prefix = '_%s__'

    gsignal('fields-filter-request', object)
    gsignal('rows-changed', object, object, str)
    # args: (row_id, row_data, name, value)
    gsignal('row-changed', int, object, str, object)

    @property
    def forms(self):
        return dict([(k, v) for k, v in self._forms.iteritems()
                if k != '__DefaultFields'])

    def __init__(self, forms, enabled_attrs, show_ids=True, **kwargs):
        self.first_selected = True
        self._forms = forms.copy()
        row_id_properties = dict(editable=False)
        if not show_ids:
            row_id_properties['show_in_gui'] = False
        self._forms['__DefaultFields'] = Form.of(Integer.named('id')\
                .using(default=0, properties=row_id_properties))

        self.uuid_mapping = dict([(name, uuid4().get_hex()[:10])
                for name in self._forms])
        self.uuid_reverse_mapping = dict([(v, k)
                for k, v in self.uuid_mapping.items()])
        self._columns = []
        self._full_field_to_field_def = {}
        if not enabled_attrs:
            enabled = lambda form_name, field: True
        else:
            enabled = lambda form_name, field:\
                    field.name in enabled_attrs.get(form_name, {})
        # Make __DefaultFields.id the first column
        form_names = ['__DefaultFields'] + sorted(forms.keys())
        for form_name in form_names:
            form = self._forms[form_name]
            for field_name in form.field_schema:
                if not form_name == '__DefaultFields' and not enabled(form_name,
                        field_name):
                    continue
                title = re.sub(r'_', ' ', field_name.name).capitalize()
                prefix = self.field_set_prefix % self.uuid_mapping[form_name] 
                name = '%s%s' % (prefix, field_name.name)
                val_type = get_type_from_schema(field_name)
                d = dict(attr=name, type=val_type, title=title, resizable=True,
                        editable=True, sorted=False)
                if field_name.properties.get('mappers', None):
                    d['mappers'] = deepcopy(field_name.properties['mappers'])
                    for m in d['mappers']:
                        m.attr = '%s%s' % (prefix, m.attr)
                if 'editable' in field_name.properties:
                    d['editable'] = field_name.properties['editable']
                if 'show_in_gui' in field_name.properties:
                    d['visible'] = field_name.properties['show_in_gui']
                if val_type == bool:
                    # Use checkbox for boolean cells
                    d['use_checkbox'] = True
                elif val_type == int:
                    # Use spinner for integer cells
                    d['use_spin'] = True
                    d['step'] = field_name.properties.get('step', 1)
                elif val_type == float:
                    # Use spinner for integer cells
                    d['use_spin'] = True
                    d['digits'] = field_name.properties.get('digits', 2)
                    d['step'] = field_name.properties.get('step', 0.1)
                self._columns.append(Column(**d))
                self._full_field_to_field_def[name] = field_name
        super(CombinedFields, self).__init__(self._columns, **kwargs)
        s = self.get_selection()
        # Enable multiple row selection
        s.set_mode(gtk.SELECTION_MULTIPLE)
        self.connect('item-changed', self._on_item_changed)
        self.connect('item-right-clicked', self._on_right_clicked)
        self.enabled_fields_by_form_name = enabled_attrs

        self.connect('item-added', lambda x, y: self.reset_row_ids())
        self.connect('item-inserted', lambda x, y, z: self.reset_row_ids())
        self.connect('item-removed', lambda x, y: self.reset_row_ids())

    def _set_rows_attr(self, row_ids, column_title, value, prompt=False):
        title_map = dict([(c.title, c.attr) for c in self.columns])
        attr = title_map.get(column_title)
        if prompt:
            Fields = Form.of(self._full_field_to_field_def[attr])
            local_field = Fields.field_schema_mapping.keys()[0]

            temp = FormViewDialog(title='Set %s' % local_field)
            response_ok, values = temp.run(Fields,
                    {local_field: value})
            if not response_ok:
                return
            value = values.values()[0]
        else:
            title_map = dict([(c.title, c.attr) for c in self.columns])
            attr = title_map.get(column_title)

        for i in row_ids:
            setattr(self[i], attr, value)
        logging.debug('Set rows attr: row_ids=%s column_title=%s value=%s'\
            % (row_ids, column_title, value))
        self._on_multiple_changed(attr)
        return True

    def _deselect_all(self, *args, **kwargs):
        s = self.get_selection()
        s.unselect_all()

    def _select_all(self, *args, **kwargs):
        s = self.get_selection()
        s.select_all()

    def _invert_rows(self, row_ids):
        self._select_all()
        s = self.get_selection()
        for i in row_ids:
            s.unselect_path(i)

    def _get_popup_menu(self, item, column_title, value, row_ids, menu_items=None):
        popup = gtk.Menu()
        def set_attr_value(*args, **kwargs):
            logging.debug('[set_attr_value] args=%s kwargs=%s' % (args, kwargs))
            self._set_rows_attr(row_ids, column_title, value)
        def set_attr(*args, **kwargs):
            logging.debug('[set_attr] args=%s kwargs=%s' % (args, kwargs))
            self._set_rows_attr(row_ids, column_title, value, prompt=True)
        def invert_rows(*args, **kwargs):
            self._invert_rows(row_ids)
        if menu_items is None:
            # Use list of tuples (menu label, callback) rather than a dict to
            # allow ordering.
            menu_items = []
        if len(row_ids) < len(self):
            menu_items += [('Select all rows', self._select_all)]
        if len(row_ids) > 0:
            menu_items += [('Deselect all rows', self._deselect_all),
                    ('Invert row selection', invert_rows)]

        item_id = [r for r in self].index(item)
        if item_id not in row_ids:
            logging.debug('[ProtocolGridController] _on_right_clicked(): '\
                            'clicked item is not selected')
        elif len(row_ids) > 1:
            menu_items += [('Set selected [%s] to "%s"' % (column_title, value),
                    set_attr_value), ('Set selected [%s] to...'''\
                            % column_title, set_attr)]

        for label, callback in menu_items:
            if label is None:
                # Assume that this should be separator
                menu_item = gtk.MenuItem()
            else:
                menu_item = gtk.MenuItem(label)
                menu_item.connect('activate', callback)
            popup.add(menu_item)
        popup.show_all()
        return popup

    def _on_right_clicked(self, list_, item, event):
        # Prevent right-click from causing selection to change
        self.stop_emission('button-press-event')

        item_spec = self.get_path_at_pos(int(event.x), int(event.y))

        if item_spec is None:
            return
        path, treeview_col, rx, ry = item_spec
        item = self._object_at_sort_path(path)
        column = treeview_col.get_data('pygtkhelpers::column')
        selection = self.get_selection()
        model, rows = selection.get_selected_rows()
        if not rows:
            row_ids = []
        else:
            row_ids = zip(*rows)[0]
        value = getattr(item, column.attr)

        self.grab_focus()
        popup = self._get_popup_menu(item, column.title, value, row_ids)
        popup.popup(None, None, None, event.button, event.time)
        return True

    def _update_row_fields(self, form_name, row_id, attrs):
        '''
        -get row values for (form_name, row_id)
        -set affected objectlist item attributes based on row values
        '''
        if form_name not in self._forms\
            or row_id >= len(self):
            return
        combined_row = self[row_id]
        form_row = combined_row.get_row_fields(form_name)

        for attr, value in attrs.items():
            setattr(form_row, attr, value)
        self.update(combined_row)

    def _on_multiple_changed(self, attr):
        selection = self.get_selection()
        model, rows = selection.get_selected_rows()
        row_ids = zip(*rows)[0]
        logging.debug('[CombinedFields] _on_multiple_changed(): attr=%s '\
                'selected_rows=%s' % (attr, row_ids))
        self.emit('rows-changed', row_ids, rows, attr)

    def _on_item_changed(self, widget, row_data, attr, value, **kwargs):
        row_id = [r for r in self].index(row_data)
        logging.debug('[CombinedFields] _on_item_changed(): name=%s value=%s'\
                % (attr, value))
        self.emit('row-changed', row_id, row_data, attr, value)

    def reset_row_ids(self):
        for i, combined_row in enumerate(self):
            combined_row.set_row_fields_attr('__DefaultFields', 'id', i + 1)


class CombinedRow(object):
    '''
    This class provides storage for all field values for a particular row
    in a CombinedFields instance.  Access to the field values is provided
    through attribute access (i.e., getattr, setattr) using the CombinedFields
    mangled field name.  This provides compatibility with the pygtkhelpers
    ObjectList class (parent class of CombinedFields), which constructs a GTK
    list view based on a list of objects corresponding to the rows.

    >>> from flatland import Form, String, Integer
    >>> from pprint import pprint

    Here we create two forms, where all fields have a default value assigned.

    >>> form1 = Form.of(String.named('my_string_field').using(default='foo'))
    >>> form2 = Form.of(Integer.named('my_int_field').using(default=10))
    >>> forms = {'example_form': form1, 'another_form': form2}

    Next, we construct a CombinedFields instance based on the forms.

    >>> combined_fields = CombinedFields(forms, enabled_attrs=None)

    Using the CombinedFields object, we create a CombinedRow instance.  Note
    that if 'attributes' is None (default), all field values will be set to
    their default values (see above).

    >>> combined_row = CombinedRow(combined_fields, attributes=None)

    Here we can see that internally, the field values corresponding to each form
    are grouped together by form into a RowFields instance.

    >>> pprint(dict([(form_name, row_fields.attrs)
    ...     for form_name, row_fields in combined_row.attributes.items()]))
    {'__DefaultFields': {'id': 0},
     'another_form': {'my_int_field': 10},
     'example_form': {'my_string_field': u'foo'}}

    Attribute access to a CombinedRow maps to the mangled field names
    defined by the CombinedFields instance.

    >>> pprint([(c.attr, c.title) for c in combined_fields._columns]) # doctest:+SKIP
    [(u'_05c880b1f4__my_int_field', u'My int field'),
    (u'_261660f830__my_string_field', u'My string field')]

    Here we read the value of the 'my_int_field' field from the 'another_form'
    using the mangled field name.

    >>> combined_row._05c880b1f4__my_int_field # doctest:+SKIP
    10

    Note that values can also be set using the mangled field name.

    >>> combined_row._05c880b1f4__my_int_field = 1234 # doctest:+SKIP

    Here we can see that the corresponding RowFields instance has been updated
    to reflect the change.

    >>> pprint(dict([(form_name, row_fields.attrs)
    ...     for form_name, row_fields in combined_row.attributes.items()])) # doctest:+SKIP
    {'another_form': {'my_int_field': 1234},
     'example_form': {'my_string_field': u'foo'}}
    '''
    field_set_prefix = '_%s__'

    def __init__(self, combined_fields, attributes=None):
        self.combined_fields = combined_fields

        self.attributes = dict()
        for form_name, form in combined_fields._forms.iteritems():
            temp = form.from_defaults()
            attr_values = dict([(k, v.value) for k, v in temp.iteritems()])
            self.attributes[form_name] = RowFields(**attr_values)
        if attributes:
            self.attributes.update(attributes)

    def set_row_fields_attr(self, form_name, attr, value):
        return setattr(self.attributes[form_name], attr, value)
    
    def get_row_fields(self, form_name):
        return self.attributes[form_name]
    
    def decode_form_name(self, mangled_form_name):
        return mangled_form_name.split('__')[-1]
    
    def set_row_id(self, row_id):
        if '__DefaultFields' in self.combined_fields._forms\
                and row_id is not None:
            self.attributes['__DefaultFields'].id = row_id

    def __getattr__(self, name):
        if not name in ['attributes', 'combined_fields']:
            for form_name, uuid_code in self.combined_fields.uuid_mapping\
                    .iteritems():
                field_set_prefix = self.field_set_prefix % uuid_code
                if name.startswith(field_set_prefix):
                    return getattr(self.attributes[form_name],
                            name[len(field_set_prefix):])
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if not name in ['attributes', 'combined_fields']:
            for form_name, uuid_code in self.combined_fields.uuid_mapping\
                    .iteritems():
                field_set_prefix = self.field_set_prefix % uuid_code
                if name.startswith(field_set_prefix):
                    # Update value
                    setattr(self.attributes[form_name],
                            name[len(field_set_prefix):], value)
                    logging.debug('[CombinedRow] setattr %s=%s' % (name, value))
                    break
        else:
            self.__dict__[name] = value

    def __str__(self):
        return '<CombinedRow attributes=%s>' % [(k, v.attrs)
                for k, v in self.attributes.iteritems()]
