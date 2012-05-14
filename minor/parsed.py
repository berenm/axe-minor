from raw import RawChunk
import struct


class Element(object):
  def __init__(self, name, width):
    self._name = name
    self._width = width
    self._data = None

  @property
  def name(self):
    return self._name


  def extract(self, raw):
    head, remains = raw.debit(1, self._width)
    self._data = head.read()
    head.close()
    return remains

  def __repr__(self):
    hexd = lambda data: ' '.join('{:02X}'.format(ord(i)) for i in data)
    return '<Element %s/%d [%s]>' % (self._name, self._width, hexd(self._data))


class Raw(Element):
  def __init__(self, name, width):
    super(Raw, self).__init__(name, width)


class FourCC(Element):
  def __init__(self, name):
    super(FourCC, self).__init__(name, 4)

  def __repr__(self):
    return '%s: "%s"' % (self._name, self._data[::-1])


class Integer(Element):
  NATIVE_ENDIAN = '='
  BIG_ENDIAN = '>'
  LITTLE_ENDIAN = '<'

  def __init__(self, name, width, signed, endian=LITTLE_ENDIAN):
    super(Integer, self).__init__(name, width)
    self._signed = signed
    self._endian = endian

    if self._signed:
      self._unpack = "bhllq"[self._width / 2]
    else:
      self._unpack = "BHLLQ"[self._width / 2]

  @property
  def value(self):
    return struct.unpack(self._endian + self._unpack, self._data)[0]

  def __repr__(self):
    return '%s: %x (%d)' % (self._name, self.value, self.value)


def int64(name):
  return Integer(name, 8, True)

def int32(name):
  return Integer(name, 4, True)

def int16(name):
  return Integer(name, 2, True)

def int8(name):
  return Integer(name, 1, True)

def uint64(name):
  return Integer(name, 8, False)

def uint32(name):
  return Integer(name, 4, False)

def uint16(name):
  return Integer(name, 2, False)

def uint8(name):
  return Integer(name, 1, False)

def beint64(name):
  return Integer(name, 8, True, Integer.BIG_ENDIAN)

def beint32(name):
  return Integer(name, 4, True, Integer.BIG_ENDIAN)

def beint16(name):
  return Integer(name, 2, True, Integer.BIG_ENDIAN)

def beint8(name):
  return Integer(name, 1, True, Integer.BIG_ENDIAN)

def beuint64(name):
  return Integer(name, 8, False, Integer.BIG_ENDIAN)

def beuint32(name):
  return Integer(name, 4, False, Integer.BIG_ENDIAN)

def beuint16(name):
  return Integer(name, 2, False, Integer.BIG_ENDIAN)

def beuint8(name):
  return Integer(name, 1, False, Integer.BIG_ENDIAN)


class Float(Element):
  def __init__(self, name, width):
    super(Float, self).__init__(name, width)
    self._unpack = "bhffd"[self._width / 2]

  def __repr__(self):
    return '%s: %f' % (self._name, struct.unpack(self._endian + self._unpack, self._data))

def double(name):
  return Float(name, 8)

def float(name):
  return Float(name, 4)

def half(name):
  return Float(name, 2)


class SizedString(Element):
  def __init__(self, name, inttype):
    super(SizedString, self).__init__(name, 0)
    self._int = inttype("size")


  def extract(self, raw):
    raw = self._int.extract(raw)
    head, remains = raw.debit(1, self._int.value)
    self._data = head.read()
    head.close()
    return remains

  @property
  def value(self):
    return str(self._data).strip('\0')

  def __repr__(self):
    return '%s: "%s"' % (self._name, self.value)


class ParsedChunk(object):
  def __init__(self, name, elements):
    self._name = name
    self._elements = elements
    self._map = dict([ (e.name, i) for i, e in enumerate(elements) ])

  def __getattribute__(self, name):
    if name != '__dict__' and name not in self.__dict__ and name in self._map:
      return self._elements[self._map[name]]
    else:
      return object.__getattribute__(self, name)

  def __repr__(self):
    return '%s:\n  %s' % (self._name, '\n  '.join([str(e) for e in self._elements]))


def parse(remains, name, elements):
  for e in elements:
    remains = e.extract(remains)

  return (ParsedChunk(name, elements), remains)
