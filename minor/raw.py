# RawChunk modelize a part of a file that hasn't been chopped yet.
# It will allow the user to chop into smaller parts, and read certain blocks.

from utils import File, Bounds

class RawChunk():
  def __init__(self, filename, bounds=Bounds(0,-1)):
  	self._file = File(filename)
  	self._bounds = bounds

  def close(self):
    self._file.close()

  @property
  def file(self):
    return self._file

  @property
  def bounds(self):
    return self._bounds

  @property
  def valid(self):
    return self._bounds.apply(self._file.length).size > 0

  @property
  def size(self):
    return self._bounds.apply(self._file.length).size

  def __repr__(self):
    return '<RawChunk %s%s>' % (self._file.name, self._bounds)


  def read(self, limit=256):
    return self._file.read(self._bounds, limit)

  def readhex(self, limit=256):
    return self._file.readhex(self._bounds, limit)


  def _split(self, position):
    # print 'D: cutting %s at %d' % (self._bounds, position)

    if not self.bounds.contains(position):
      before, after = (RawChunk(self._file.name, self._bounds), None)
    else:
      before = RawChunk(self._file.name, Bounds(self._bounds.start, position - 1))
      after = RawChunk(self._file.name, Bounds(position, self._bounds.end))
      before = before.valid and before or None
      after = after.valid and after or None

    self.close()
    return (before, after)

  def chop(self, bounds):
    before, remains = self._split(bounds.start)
    if remains is None:
      chopped, after = (None, None)
    else:
      chopped, after = remains._split(bounds.end + 1)

    return (before, chopped, after)

  def cutat(self, position):
    return self._split(position)

  def debit(self, count, chopsize):
    chops = []
    remains = self

    for i in range(0, count):
      if remains is not None and remains.valid:
        head, remains = remains._split(remains.bounds.start + chopsize)
        chops.append(head)

    chops.append(remains)
    return chops

  def divide(self, count):
    chopsize = max(self.size / count, 1)
    return self.debit(count, chopsize)

# r = RawChunk("test/data")
# print r
# print r.bounds.size
# print r.size
# print [ r.read() for r in r.debit(1, -1) ]