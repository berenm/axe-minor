#!/usr/bin/python

import os
import sys

import ui
from minor.raw import RawChunk

from gi.repository import Gtk, GtkSource, GObject


# builder = Gtk.Builder()
# builder.add_from_file('Test.ui')
# builder.connect_signals(Window())

# window = builder.get_object('TestWindow')
# window.show()

# m = window.get_child().get_child().get_model()
# m.append(None, ['test', long(10)])
# r = m.append(None, ['test', long(10)])
# m.append(r, ['test', long(10)])

# Gtk.main()

if len(sys.argv) > 1:
  hexui = ui.HexDumpUi(RawChunk(sys.argv[1]))
  hexui.window.show()

  Gtk.main()

else:
  winui = ui.WindowUi()
  winui.window.show()

  Gtk.main()
