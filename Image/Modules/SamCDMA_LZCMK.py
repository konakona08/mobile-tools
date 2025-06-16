from io import BytesIO
import struct

def decode(in_data, out_data, out_size, is_12bpp = False):
    in_data = BytesIO(in_data)
    temp_prev = bytearray(out_size)
    for i in range(min(len(out_data), out_size)):
        temp_prev[i] = out_data[i]
    
    if is_12bpp:
        marker = 0xffff
    else:
        marker = struct.unpack("<H", in_data.read(2))[0]

    dec_size = 0

    while dec_size < out_size:
        try:
            check = struct.unpack("<H", in_data.read(2))[0]
            if check == marker:
                mlen, offset = struct.unpack("<HH", in_data.read(4))
                read_off = (offset&0x7fff)<<1
                if offset>>15:
                    src = temp_prev
                else:
                    src = out_data
                out_data[dec_size:dec_size+(mlen<<1)] = src[read_off:read_off+(mlen<<1)]
                dec_size += mlen<<1
            else:
                out_data[dec_size:dec_size+2] = struct.pack("<H", check)
                dec_size += 2
        except:
            break
            