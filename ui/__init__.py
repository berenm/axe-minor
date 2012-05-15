from gi.repository import Gtk

class Ui(object):
  def __init__(self, uifile):
    self._widgets = {}
    self._builder = Gtk.Builder()

    super(Ui, self).__init__()

    self._builder.add_from_file(uifile)
    self._builder.connect_signals(self)

    for o in self._builder.get_objects():
      if isinstance(o, Gtk.Buildable):
        self._widgets[Gtk.Buildable.get_name(o)] = o

  def __getattribute__(self, name):
    if name == '__dict__' or name in self.__dict__:
      return super(Ui, self).__getattribute__(name)

    elif name in self._widgets:
      return self._widgets[name]

    else:
      return super(Ui, self).__getattribute__(name)

  def on_quit(self, widget):
    Gtk.main_quit()

from Window import WindowUi
from HexDump import HexDumpUi
from TreeView import TreeViewUi
