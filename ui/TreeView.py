from gi.repository import Gtk

from . import Ui

class TreeViewUi(Ui):
  def __init__(self):
    super(TreeViewUi, self).__init__('ui/TreeView.ui')
