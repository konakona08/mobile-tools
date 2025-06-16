from io import BytesIO
import struct

def rgb444_to_565(pixel):
    r = ((pixel&0xf00)>>8)<<1
    g = ((pixel&0x0f0)>>4)<<2
    b = ((pixel&0x00f)<<1)
    return (r<<11)|(g<<5)|b

def decode(in_data, out_data, out_size):
    in_data = BytesIO(in_data)

    dec_size = 0

    while dec_size < out_size:
        try:
            pixel = struct.unpack("<H", in_data.read(2))[0]
            pixel_out = rgb444_to_565(pixel>>4)
            count = (pixel&0xf) + 1
            for _ in range(count):
                out_data[dec_size:dec_size+2] = struct.pack("<H", pixel_out)
                dec_size += 2
        except:
            break