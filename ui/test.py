#!/usr/bin/python

import os
import sys
from gi.repository import Gtk, GtkSource, GObject

def get_child_by_name(parent, name):
    """
    Iterate through a gtk container, `parent`, 
    and return the widget with the name `name`.
    """
    def iterate_children(widget, name):
        if widget.get_name() == name:
            return widget
        try:
            for w in widget.get_children():
                result = iterate_children(w, name)
                if result is not None:
                    return result
                else:
                    continue
        except AttributeError:
            pass
    return iterate_children(parent, name)

class Window(object):
  def on_destroy(self, obj):
  	print self, obj
	Gtk.main_quit()

  def on_check_resize(self, obj, var):
  	print self, obj, var.x, var.y, var.width, var.height
	lineview = obj.get_child1()
	dataview = obj.get_child2()
	hexwidth = dataview.get_position()
	ascwidth = dataview.get_allocated_width() - dataview.get_position()

	bytesperline = ascwidth / 7
	bytesperline = min(bytesperline, (hexwidth / 7 + 1) / 3)

	f = File('test.py')
	d = f.readhex(Bounds(0, -1), bytesperline)
	lineview.get_buffer().set_text(d[0])
	hexview.get_buffer().set_text(d[1])
	ascview.get_buffer().set_text(d[2])

	bounds = lineview.get_buffer().get_bounds()
	lineview.get_buffer().apply_tag_by_name('text', bounds[0], bounds[1])
	bounds = hexview.get_buffer().get_bounds()
	hexview.get_buffer().apply_tag_by_name('text', bounds[0], bounds[1])
	bounds = ascview.get_buffer().get_bounds()
	ascview.get_buffer().apply_tag_by_name('text', bounds[0], bounds[1])

	print bytesperline

class File:
  _files = {}

  def __init__(self, name, length=None):
    self._name = name
    if self._name in File._files:
      self._file = File._files[self._name]
    else:
      self._file = open(self._name, 'rb')
      File._files[self._name] = self._file

    if length is None:
      self._file.seek(0, os.SEEK_END)
      self._length = self._file.tell()
      self._file.seek(0, os.SEEK_SET)
    else:
      self._length = length

  @property
  def name(self):
    return self._name

  @property
  def length(self):
    return self._length


  def read(self, bounds):
    bounds = bounds.apply(self._length)
    
    self._file.seek(bounds.start, os.SEEK_SET)
    # print 'D: reading %s (len: %d) from %d to %d' % (self._name, self._length, bounds.start, bounds.end)

    count, append = (bounds.size, '')
    return self._file.read(count) + append

  def readhex(self, bounds, bytesperline=16):
    binary = self.read(bounds)

    hexd = lambda data: ' '.join('{:02X}'.format(ord(i)) for i in data)
    ascd = lambda data: ''.join(31 < ord(i) < 127 and i or '.' for i in data)

    linedump, hexdump, asciidump = ('', '', '')
    for line in range(0, len(binary), bytesperline):
      data = binary[line : line + bytesperline]
      linedump, hexdump, asciidump = (linedump + '\n', hexdump + '\n', asciidump + '\n')
      linedump, hexdump, asciidump = (linedump + '{:08X}'.format(line), hexdump + '{}'.format(hexd(data)), asciidump + '{}'.format(ascd(data)))
    
    linedump, hexdump, asciidump = (linedump.strip('\n'), hexdump.strip('\n'), asciidump.strip('\n'))
    return (linedump, hexdump, asciidump)

  def close(self):
    pass

class Bounds():
  def __init__(self, start, end):
    self._start = start
    self._end = end

  @property
  def crossed(self):
    return (self._start < 0) != (self._end < 0)

  @property
  def start(self):
    return self._start

  @property
  def end(self):
    return self._end

  @property
  def size(self):
    if self.crossed:
      return -1
    else:
      return self._end - self._start + 1

  def contains(self, position):
    if not self.crossed:
      return self._start <= position <= self._end
    else:
      return self._start <= position or position <= self._end

  def __repr__(self):
    return '[%d,%d]' % (self._start, self._end)


  def apply(self, length):
    start = self._start
    start += start < 0 and length or 0

    end = self._end
    end += end < 0 and length or 0

    return Bounds(start, end)

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

if sys.argv[1] == 'hex':
  GObject.type_register(GtkSource.View)

  builder = Gtk.Builder()
  builder.add_from_file('HexDump.ui')

  window = builder.get_object('window')
  paned = window.get_child().get_child()
  lineview = paned.get_child().get_child1()
  hexview = paned.get_child().get_child2().get_child1()
  ascview = paned.get_child().get_child2().get_child2()

  # lm = GtkSource.LanguageManager.get_default()
  # lineview.set_buffer(GtkSource.Buffer.new_with_language(lm.get_language("python")))
  # hexview.set_buffer(GtkSource.Buffer.new_with_language(lm.get_language("python")))
  # ascview.set_buffer(GtkSource.Buffer.new_with_language(lm.get_language("python")))

  tt = builder.get_object('texttagtable')
  lineview.get_buffer().create_tag(tag_name='text', font='Monospace 8')
  hexview.get_buffer().create_tag(tag_name='text', font='Monospace 8')
  ascview.get_buffer().create_tag(tag_name='text', font='Monospace 8')

  f = File('test.py')
  d = f.readhex(Bounds(0, -1))
  lineview.get_buffer().set_text(d[0])
  hexview.get_buffer().set_text(d[1])
  ascview.get_buffer().set_text(d[2])

  bounds = lineview.get_buffer().get_bounds()
  lineview.get_buffer().apply_tag_by_name('text', bounds[0], bounds[1])
  bounds = hexview.get_buffer().get_bounds()
  hexview.get_buffer().apply_tag_by_name('text', bounds[0], bounds[1])
  bounds = ascview.get_buffer().get_bounds()
  ascview.get_buffer().apply_tag_by_name('text', bounds[0], bounds[1])

  builder.connect_signals(Window())
  window.show()
  Gtk.main()

else:
  GObject.type_register(GtkSource.View)

  builder = Gtk.Builder()
  builder.add_from_file('Window.ui')

  window = builder.get_object('window')
  tb = window.get_child().get_children()[0].get_children()[1]
  toolbar = builder.get_object('toolbar')
  toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

  for o in builder.get_objects():
    print Gtk.Buildable.get_name(o)

  builder.connect_signals(Window())
  window.show()
  Gtk.main()
