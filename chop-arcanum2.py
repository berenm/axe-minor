#!/usr/bin/python

import os
import sys
import binascii
import zlib
import struct

from pprint import pprint

from minor.raw import RawChunk
from minor.utils import Bounds, File

class chunk(object):
  def __init__(self, name, fields=[], **kvargs):
    super(chunk, self).__init__()
    self._name = name

    self._start = kvargs.pop('start', None)
    self._end = kvargs.pop('end', None)
    self._size = kvargs.pop('size', None)

    self.add_children(fields)

    if self._size is None and all([not callable(c._size) for c in self._children]):
      self._size = sum([c.size for c in self._children])

  def add_children(self, fields):
    self._children = []
    for i, v in enumerate(fields):
      if v._name in self.__dict__:
        raise Exception('Field name already defined %s' % v._name)

      self.__dict__[v._name] = v
      self._children.append(v)

  def link(self, parent=None, prev=None, next=None):
    if parent is not None:
      self._root = parent._root
    else:
      self._root = self

    self._parent = parent
    self.prev = prev
    self.next = next

    if not self.has_bounds:
      if self.has_size:
        if self.prev is None and self.parent.has_start:
          print '%s: hooked start to parent.start' % self.fullname
          self._start = self.parent._start

        elif self.next is None and self.parent.has_end:
          print '%s: hooked end to parent.end' % self.fullname
          self._end = self.parent._end

        elif self.prev is not None and self.prev.has_bounds:
          print '%s: hooked start to prev.end' % self.fullname
          self._start = lambda s: s.prev.end + 1
        
        elif self.next is not None and self.next.has_bounds:
          print '%s: hooked end to next.start' % self.fullname
          self._end = lambda s: s.next.start - 1
        
        else:
          raise Exception("%s cannot be hooked on parent, prev or next" % self.fullname)

      elif self.has_start:
        if self.next is None and self.parent.has_end:
          print '%s: hooked end to parent.end' % self.fullname
          self._end = self.parent._end

        elif self.next is not None and self.next.has_bounds:
          print '%s: hooked end to next.start' % self.fullname
          self._end = lambda s: s.next.start - 1
        
        else:
          self._size = lambda s: sum([c.size for _,c in s.children])

      elif self.has_end:
        if self.prev is None and self.parent.has_start:
          print '%s: hooked start to parent.start' % self.fullname
          self._start = self.parent._start

        elif self.prev is not None and self.prev.has_bounds:
          print '%s: hooked start to prev.end' % self.fullname
          self._start = lambda s: s.prev.end + 1

        else:
          self._size = lambda s: sum([c.size for _,c in s.children])

      else:
        if self.prev is None and self.next is None:
          print '%s: start = parent.start, end = parent.end' % self.fullname
          self._start = self.parent._start
          self._end = self.parent._end
        
        elif self.next is None:
          print '%s: end = parent.end, size = sum(children.size)' % self.fullname
          self._end = self.parent._end
          self._size = lambda s: sum([c.size for _,c in s.children])

        elif self.prev is None:
          print '%s: start = parent.start, size = sum(children.size)' % self.fullname
          self._start = self.parent._start
          self._size = lambda s: sum([c.size for _,c in s.children])

        else:
          print '%s: start = prev.end + 1, size = sum(children.size)' % self.fullname
          self._start = lambda s: s.prev.end + 1
          self._size = lambda s: sum([c.size for _,c in s.children])

    self.link_children()

  def link_children(self):
    for i, c in self.children:
      prev = None
      if i > 0:
        prev = self._children[i - 1]

      next = None
      if i < len(self._children) - 1:
        next = self._children[i + 1]

      c.link(self, prev, next)

  def parse(self):
    print '%s: parsing...' % self.fullname
    self._start = self.start
    self._end = self.end
    self._size = self.size
    self.parse_children()

  def parse_children(self):
    for i, c in self.children:
      c.parse()

  @property
  def fullname(self):
    output = ''
    if self._parent is not None:
      output += self._parent.fullname + '.'
    return output + self._name

  @property
  def first(self):
    if len(self._children) == 0:
      return None
    return self._children[0]

  @property
  def last(self):
    if len(self._children) == 0:
      return None
    return self._children[len(self._children) - 1]

  @property
  def children(self):
    if len(self._children) == 0:
      return []
    order = self.has_end and -1 or 1
    return [ (_i, _c) for _i, _c in enumerate(self._children)][::order]

  @property
  def parent(self):
    return self._parent

  @property
  def root(self):
    return self._root

  @property
  def file(self):
    return self.root.file

  @property
  def data(self):
    return self.file.read(self.bounds)

  @property
  def hexdata(self):
    return self.file.readhexs(self.bounds, 256)[1:]

  def debug(self, i=''):
    print i, self._name, self.hexdata
    for c in self._children:
      c.debug(i + '  ')

  @property
  def bounds(self):
    return Bounds(self.start, self.end)

  @property
  def has_bounds(self):
    return self.has_start and self.has_end or self.has_start and self.has_size or self.has_end and self.has_size

  @property
  def has_start(self):
    return self._start is not None

  @property
  def start(self):
    if self.has_start:
      if callable(self._start):
        return self._start(self)
      else:
        return self._start
    elif self.has_end and self.has_size:
      return self.end - self.size + 1

  @property
  def has_end(self):
    return self._end is not None

  @property
  def end(self):
    if self.has_end:
      if callable(self._end):
        return self._end(self)
      else:
        return self._end
    elif self.has_start and self.has_size:
      return self.start + self.size - 1

  @property
  def has_size(self):
    return self._size is not None

  @property
  def size(self):
    if self.has_size:
      if callable(self._size):
        return self._size(self)
      else:
        return self._size
    elif self.has_start and self.has_end:
      return self.end - self.start + 1


class root(chunk):
  def __init__(self, fields=[], **kvargs):
    s = self
    self._parent = None

    if 'start' not in kvargs:
      kvargs['start'] = 0

    if 'end' not in kvargs:
      kvargs['end'] = -1

    super(root, self).__init__('root', fields, **kvargs)

    self._file = None

  @property
  def file(self):
    return self._file

  def parse(self, filename):
    self._file = File(filename)
    for i, c in self.children:
      c.parse()


class sequence(chunk):
  def __init__(self, name, **kvargs):
    self.count = kvargs.pop('count', None)
    self.item = kvargs.pop('item', None)
    super(sequence, self).__init__(name, **kvargs)

  def parse(self):
    fields = [self.item(self, 'entry-' + str(k)) for k in range(self.count(self))]
    self.add_children(fields)
    self.link_children()
    super(sequence, self).parse()


class dummy(chunk):
  def __init__(self, **kvargs):
    super(dummy, self).__init__('dummy', **kvargs)


class uint32(chunk):
  def __init__(self, name):
    super(uint32, self).__init__(name, size=4)

  @property
  def value(self):
    return struct.unpack('I', self.data)[0]

class bytes(chunk):
  def __init__(self, name, length):
    super(bytes, self).__init__(name, size=length)

class sized_string(chunk):
  def __init__(self, name, length_type):
    super(sized_string, self).__init__(name, [length_type('length')], size=lambda s: s.length.value + s.length.size)

class fourcc(chunk):
  def __init__(self, name):
    super(fourcc, self).__init__(name, size=4)


p = root([
  chunk('data',
    end=lambda s: s.root.index.start
  ),
  chunk('index', [
      uint32('count'),
      sequence('entries',
        count=lambda s: s.root.index.count.value,
        item=lambda s, n: chunk(n, [
          sized_string('name', uint32),
          uint32('name_address'),
          uint32('flags'),
          uint32('decompressed_size'),
          uint32('compressed_size'),
          uint32('data_offset')
        ])
      )
    ],
    start=lambda s: -s.root.footer.index_size.value,
    size=lambda s: s.root.footer.index_size.value - 28,
  ),
  chunk('footer', [
      bytes('uuid', 16),
      fourcc('magic'),
      uint32('filename_size'),
      uint32('index_size')
    ],
    end=-1
  )
])

p.link()
p.parse(sys.argv[1])
print p.footer.index_size.value
print p.index.count.value
p.index.debug()

# def chop(raw_chunks=[], chopped=[]):
#   return (raw_chunks, chopped)

# def open_file(file_name):
#   return RawChunk(file_name)

# remains = open_file(sys.argv[1])

# before, chopped, remains = remains.chop(Bounds(-28, -1))
# assert(remains is None)

# footer, remains = parse(chopped, "footer", [Raw("UUID (CoCreateGuid)",16), FourCC("magic"), uint32("filename_size"), uint32("index_offset")])
# assert(remains is None)

# before, remains = before.cutat(-footer.index_offset.value)
# index, remains = parse(remains, "index", [int32("count")])

# entries = []
# for i in range(0, index.count.value):
#   entry, remains = parse(remains, "entry", [SizedString("name", uint32), uint32("name_address"), uint32("flags"), uint32("decompressed_size"), uint32("compressed_size"), uint32("data_offset")])
#   entries.append(entry)
# assert(remains is None)

# print footer
# print "expecting %d entries" % ((footer.index_offset.value - 32 - footer.filename_size.value) / 24)
# print index

# output = sys.argv[2]
# for e in entries:
#   target = os.path.join(output, e.name.value.replace('\\', '/'))
#   print '.. extracting %s to %s...' % (e.name.value, target)

#   if e.flags.value == 1024: # folder
#     if not os.path.exists(target):
#       os.makedirs(target)

#   elif e.flags.value == 2:  # compressed file
#     if not os.path.exists(os.path.dirname(target)):
#       os.makedirs(os.path.dirname(target))

#     with open(target, 'wb') as o:
#       i = RawChunk(sys.argv[1], Bounds(e.data_offset.value, e.data_offset.value + e.compressed_size.value - 1))
#       o.write(zlib.decompress(i.read(None)))
#   elif e.flags.value == 1:  # uncompressed file
#     if not os.path.exists(os.path.dirname(target)):
#       os.makedirs(os.path.dirname(target))

#     with open(target, 'wb') as o:
#       i = RawChunk(sys.argv[1], Bounds(e.data_offset.value, e.data_offset.value + e.compressed_size.value - 1))
#       o.write(i.read(None))
#   else:
#     print e.flags

# print 'read: %d entries' % len(entries)
