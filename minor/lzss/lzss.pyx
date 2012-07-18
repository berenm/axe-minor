import struct

from libc.stdio cimport printf
from libc.stdlib cimport free

cdef extern from "lzss.h":
  size_t c_decompress_block(unsigned char* input, size_t input_len, unsigned char* output, size_t output_len)

def decompress_block(input):
  cdef bytes input_bytes = input
  cdef unsigned char* c_input = input_bytes
  cdef bytes output_bytes
  cdef unsigned char* c_output
  cdef int output_size = -1
  
  output = ""
  output_length = len(input) * 10
  while output_size < 0:
    output = output_length * '\0'
    output_bytes = output
    c_output = output_bytes

    output_size = c_decompress_block(c_input, len(input), c_output, len(output))
    output_length = output_length * 3 / 2

  return output[:output_size]

def decompress(input, output):
  while input is not None and input.size > 0:
    short, input = input.debit(1, 2)
    bytes = struct.unpack(">h", short.read(None))[0]
    if bytes == 0:
      break

    elif bytes < 0:
      data, input = input.debit(1, -bytes)
      output.write(data.read(None))

    elif bytes > 0:
      data, input = input.debit(1, bytes)
      output.write(decompress_block(data.read(None)))

  return output