
"""Reusable components, Delegate Example 1
"""
import gtk
from pyGtkhelpers.delegates import WindowView

class UserView(WindowView):
    """The user interface for my user management program"""

if __name__ == '__main__':
    UserView().show_and_run()

