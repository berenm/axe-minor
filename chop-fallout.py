#!/usr/bin/python

import os
import sys
import binascii

from minor import lzss
from minor.raw import RawChunk
from minor.parsed import *
from minor.utils import Bounds

def chop(raw_chunks=[], chopped=[]):
  return (raw_chunks, chopped)

def open_file(file_name):
  return RawChunk(file_name)

remains = open_file(sys.argv[1])
header, remains = parse(remains, "header", [beuint32("folder_count"), beuint32("unknown"), beuint32("unknown"), beuint32("timestamp")])
frm = remains.bounds.start

folders = []
for i in range(0, header.folder_count.value):
  f, remains = parse(remains, "folder", [SizedString("name", uint8)])
  folders.append(f)

output = sys.argv[2]
for i in range(0, header.folder_count.value):
  f = folders[i]
  files_header, remains = parse(remains, "files", [beuint32("count"), beuint32("unknown"), beuint32("flags"), beuint32("timestamp")])

  entries = []
  for i in range(0, files_header.count.value):
    e, remains = parse(remains, "entry", [SizedString("name", uint8), beuint32("flags"), beuint32("offset"), beuint32("size"), beuint32("packed_size")])
    entries.append(e)

    source = os.path.join(f.name.value.replace('\\', '/'), e.name.value.replace('\\', '/'))
    target = os.path.join(output, source)
    print '.. extracting %s to %s...' % (source, target)

    if e.flags.value == 64:  # compressed file
      if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))

      with open(target, 'wb') as o:
        i = RawChunk(sys.argv[1], Bounds(e.offset.value, e.offset.value + e.packed_size.value - 1))
        lzss.decompress(i, o)

    elif e.flags.value == 32:  # uncompressed file
      if not os.path.exists(os.path.dirname(target)):
        os.makedirs(os.path.dirname(target))

      with open(target, 'wb') as o:
        i = RawChunk(sys.argv[1], Bounds(e.offset.value, e.offset.value + e.size.value - 1))
        o.write(i.read(None))

    else:
      print e.flags

  print 'read: %d entries' % len(entries)


