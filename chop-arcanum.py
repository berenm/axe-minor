#!/usr/bin/python

import sys
import binascii

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

footer, remains = parse(chopped, "footer", [Raw("UUID (CoCreateGuid)",16), FourCC("magic"), Raw("unknown",4), uint32("index_size")])
assert(remains is None)

before, remains = before.cutat(-footer.index_size.value)
index, remains = parse(remains, "index", [int32("count")])

entries = []
for i in range(0, index.count.value):
  entry, remains = parse(remains, "entry", [SizedString("name", uint32), Raw("uuid?", 4), Raw("unknown",4), uint32("decompressed_size"), uint32("compressed_size"), uint32("data_offset")])
  entries.append(entry)
assert(remains is None)

print footer
print index
for e in entries:
  print e
print 'read: %d entries' % len(entries)
