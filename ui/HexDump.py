from gi.repository import Gtk

from . import Ui
from minor import utils

class HexDumpUi(Ui):
  def __init__(self, chunk):
    super(HexDumpUi, self).__init__('ui/HexDump.ui')

    self._chunk = chunk

    self.linebuffer = self.lineview.get_buffer()
    self.hexbuffer = self.hexview.get_buffer()
    self.ascbuffer = self.ascview.get_buffer()

    self.linebuffer.create_tag(tag_name='text', font='Monospace 8')
    self.hexbuffer.create_tag(tag_name='text', font='Monospace 8')
    self.ascbuffer.create_tag(tag_name='text', font='Monospace 8')


  def on_resize(self, widget, extends):
    hexwidth = self.datapaned.get_position()
    ascwidth = self.datapaned.get_allocated_width() - self.datapaned.get_position()

    bytesperline = ascwidth / 7
    bytesperline = min(bytesperline, (hexwidth / 7 + 1) / 3)

    (linedata, hexdata, ascdata) = self._chunk.readhexs(utils.Bounds(0, -1), bytesperline)
    self.linebuffer.set_text(linedata)
    self.hexbuffer.set_text(hexdata)
    self.ascbuffer.set_text(ascdata)

    b = self.linebuffer.get_bounds()
    self.linebuffer.apply_tag_by_name('text', b[0], b[1])

    b = self.hexbuffer.get_bounds()
    self.hexbuffer.apply_tag_by_name('text', b[0], b[1])

    b = self.ascbuffer.get_bounds()
    self.ascbuffer.apply_tag_by_name('text', b[0], b[1])
