from pyGtkHelpers.ui.objectlist import ObjectList, ObjectTree, Column


class User(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age


items = [
    Column('name', str, editable=True, searchable=True),
    Column('age', int),
    Column('expander', expander=True),
]


def pytest_generate_tests(metafunc):
    if ('items' in metafunc.funcargnames or
            'searchcheck' in metafunc.funcargnames):
        if not hasattr(metafunc.function, 'tree_only'):
            metafunc.addcall(id='list', param=ObjectList)
        if not hasattr(metafunc.function, 'list_only'):
            metafunc.addcall(id='tree', param=ObjectTree)


def pytest_funcarg__items(request):
    return request.param(items)


user = User(name='Hans', age=10)
user2 = User(name='Gretel', age=11)
user3 = User(name='Witch', age=409)
