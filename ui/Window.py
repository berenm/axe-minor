from gi.repository import Gtk

from . import Ui

class WindowUi(Ui):
  def __init__(self):
    super(WindowUi, self).__init__('ui/Window.ui')

    self.toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
