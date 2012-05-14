import sys
import os
import logging

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


  def read(self, bounds, limit):
    bounds = bounds.apply(self._length)
    
    self._file.seek(bounds.start, os.SEEK_SET)
    # print 'D: reading %s (len: %d) from %d to %d' % (self._name, self._length, bounds.start, bounds.end)

    count, append = (bounds.size, '')
    if count > limit:
      count, append = (limit, '...')

    return self._file.read(count) + append

  def readhex(self, bounds, limit):
    binary = self.read(bounds, limit)

    hexd = lambda data: ' '.join('{:02X}'.format(ord(i)) for i in data)
    ascd = lambda data: ''.join(31 < ord(i) < 127 and i or '.' for i in data)

    dump = ''
    for line in range(0, len(binary), 16):
      data = binary[line : line + 16]
      dump = dump + '\n{:08X} | {:47} | {}'.format(line, hexd(data), ascd(data))
    
    if len(dump) > 0:
      dump = dump[1:]
    return dump

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
