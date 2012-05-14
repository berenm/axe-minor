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
header, remains = parse(remains, "header", [beuint32("folder_count"), beuint32("unknown"), beuint32("unknown"), beuint32("timestamp?")])
print header

for i in range(0, header.folder_count.value):
  folder, remains = parse(remains, "folder", [SizedString("name", uint8)])
  print i, folder

print remains.readhex()

for i in range(0, header.folder_count.value):
  files_header, remains = parse(remains, "files", [beuint32("count"), beuint32("unknown"), beuint32("flags"), beuint32("timestamp?")])
  print files_header
  entries = []
  for i in range(0, files_header.count.value):
    entry, remains = parse(remains, "entry", [SizedString("name", uint8), beuint32("flags"), beuint32("offset"), beuint32("unknown"), beuint32("size")])
    entries.append(entry)
    print i, entry

  print 'read: %d entries' % len(entries)

print remains
print remains.readhex()