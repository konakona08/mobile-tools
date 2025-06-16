from io import BytesIO
import struct

def decode(in_data, out_data, out_size):
    in_data = BytesIO(in_data)

    while dec_size < out_size:
        pixel = struct.unpack("<H", in_data.read(2))[0]
        if pixel == 0xf000:
            count = struct.unpack("<H", in_data.read(2))[0]
            pixel = struct.unpack("<H", in_data.read(2))[0]
            for _ in range(count):
                out_data[dec_size:dec_size+2] = struct.pack("<H", pixel)
                dec_size += 2
        else:
            out_data[dec_size:dec_size+2] = struct.pack("<H", pixel)
            dec_size += 2