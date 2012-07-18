#include <stdint.h>

size_t c_decompress_block(uint8_t* input, size_t input_length, uint8_t* output, size_t output_length) {
    static int8_t const min_length = 3;
    static int8_t const max_length = 18;
    static int32_t const dict_size = 4096;

    size_t dict_read = 0;
    size_t dict_write = dict_size - max_length;

    uint8_t dictionary[dict_size];
    memset(dictionary, dict_size, ' ');
    
    uint8_t* const input_end = input + input_length;
    uint8_t* const output_start = output;
    uint8_t* const output_end = output + output_length;

    uint16_t flags = 0;
    while(input < input_end) {
      flags >>= 1;

      if ((flags & 0x100) == 0) {
        if (input == input_end)
          break;

        flags = (uint16_t) *(input++);
        flags |= 0xFF00;
      }

      if (flags & 1) {
        if (input == input_end)
          break;
        if (output == output_end)
          return -1;

        uint8_t byte = *(input++);
        *(output++) = byte;
        dictionary[(dict_write++) % dict_size] = byte;
        dict_write %= dict_size;

      } else {
        if (input >= input_end - 1)
          break;

        dict_read = (size_t) *(input++);
        size_t length = (size_t) *(input++);

        dict_read |= (length & 0xF0) << 4;
        length &= 0x0F;
        length += min_length;

        size_t i;
        for (i = 0; i < length; ++i) {
          if (output == output_end)
            return -1;

          uint8_t byte = dictionary[(dict_read++) % dict_size];
          *(output++) = byte;
          dictionary[(dict_write++) % dict_size] = byte;

          dict_read %= dict_size;
          dict_write %= dict_size;
        }
      }
    }

    return output - output_start;
}