#!/usr/bin/python

import os
import sys
import binascii
import zlib

from minor.raw import RawChunk
from minor.parsed import *
from minor.utils import Bounds

def chop(raw_chunks=[], chopped=[]):
  return (raw_chunks, chopped)

def open_file(file_name):
  return RawChunk(file_name)

remains = open_file(sys.argv[1])

before, chopped, remains = remains.chop(Bounds(-28, -1))
assert(remains is None)

footer, remains = parse(chopped, "footer", [Raw("UUID (CoCreateGuid)",16), FourCC("magic"), uint32("filename_size"), uint32("index_offset")])
assert(remains is None)

before, remains = before.cutat(-footer.index_offset.value)
index, remains = parse(remains, "index", [int32("count")])

entries = []
for i in range(0, index.count.value):
  entry, remains = parse(remains, "entry", [SizedString("name", uint32), uint32("name_address"), uint32("flags"), uint32("decompressed_size"), uint32("compressed_size"), uint32("data_offset")])
  entries.append(entry)
assert(remains is None)

print footer
print "expecting %d entries" % ((footer.index_offset.value - 32 - footer.filename_size.value) / 24)
print index

output = sys.argv[2]
for e in entries:
  target = os.path.join(output, e.name.value.replace('\\', '/'))
  print '.. extracting %s to %s...' % (e.name.value, target)

  if e.flags.value == 1024: # folder
    if not os.path.exists(target):
      os.makedirs(target)

  elif e.flags.value == 2:  # compressed file
    if not os.path.exists(os.path.dirname(target)):
      os.makedirs(os.path.dirname(target))

    with open(target, 'wb') as o:
      i = RawChunk(sys.argv[1], Bounds(e.data_offset.value, e.data_offset.value + e.compressed_size.value - 1))
      o.write(zlib.decompress(i.read(None)))
  elif e.flags.value == 1:  # uncompressed file
    if not os.path.exists(os.path.dirname(target)):
      os.makedirs(os.path.dirname(target))

    with open(target, 'wb') as o:
      i = RawChunk(sys.argv[1], Bounds(e.data_offset.value, e.data_offset.value + e.compressed_size.value - 1))
      o.write(i.read(None))
  else:
    print e.flags

print 'read: %d entries' % len(entries)
